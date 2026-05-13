# -*- coding: UTF-8 -*-
import addonHandler, config, core, globalPluginHandler, speech, speech.manager, textInfos, types, ui, wx
from gui import settingsDialogs
from logHandler import log

addonHandler.initTranslation()

characterDescriptionTimer = None
# Suppress timer cancellation during calls to speak() and speakSpelling()
# that originate from within speakTextInfo itself, so they do not
# inadvertently cancel the timer we are about to set.
_suppressCancelInSpeak = False
# Incremented each time a new timer is scheduled or cancelled.
# speakDelayedDescription compares its own snapshot of this value against
# the current one and silently returns if they differ, making any callback
# that was already queued in the wx event loop a no-op.
_timerGeneration = 0

confspec = {
    "delay": "integer(default=1000)",
}
config.conf.spec["setDescriptionDelay"] = confspec

# Name of the add-on that conflicts with this one by patching the same speech functions.
_CONFLICTING_ADDON_NAME = "EnhancedPhoneticReading"


class _ConflictWarningDialog(wx.Dialog):
    """A non-modal dialog that warns the user about a conflicting add-on.

    Using Show() instead of ShowModal() keeps NVDA fully responsive while
    the dialog is open.
    """

    def __init__(self, title, message):
        super().__init__(
            parent=None,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP,
        )
        sizer = wx.BoxSizer(wx.VERTICAL)

        text = wx.StaticText(self, label=message)
        text.Wrap(400)
        sizer.Add(text, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)

        # Translators: OK button label on the conflict warning dialog.
        okBtn = wx.Button(self, wx.ID_OK, label=_("OK"))
        okBtn.SetDefault()
        sizer.Add(okBtn, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

        self.SetSizerAndFit(sizer)
        self.CentreOnScreen()

        okBtn.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
        self.Bind(wx.EVT_CLOSE, lambda evt: self.Destroy())


def _checkConflictingAddon():
    """Check whether the conflicting add-on is installed and warn the user if so.

    The check is scheduled via core.callLater to ensure the wx GUI is fully
    initialised before attempting to show the warning.

    When a conflict is detected:
    - ui.message() reads the warning aloud via NVDA without blocking.
    - A non-modal wx.Dialog provides a visible reminder without freezing NVDA.
    """
    try:
        installedAddons = addonHandler.getAvailableAddons()
        names = [addon.name for addon in installedAddons]
    except Exception:
        log.warning(
            "setDescriptionDelay: could not retrieve installed add-on list "
            "while checking for conflicts."
        )
        return

    if _CONFLICTING_ADDON_NAME not in names:
        return

    log.warning(
        f"setDescriptionDelay: conflicting add-on '{_CONFLICTING_ADDON_NAME}' "
        "is installed. Both add-ons patch the same speech functions, which may "
        "cause unpredictable behaviour."
    )

    # Translators: Title of the conflict warning dialog.
    title = _("Add-on Conflict Warning")
    # Translators: Body of the conflict warning dialog shown when
    # EnhancedPhoneticReading is detected alongside setDescriptionDelay.
    message = _(
        "The add-on '{conflicting}' is also installed.\n\n"
        "Both '{conflicting}' and 'setDescriptionDelay' modify the same "
        "internal speech functions, which can cause unpredictable behaviour "
        "such as doubled speech, missed character descriptions, or crashes.\n\n"
        "Please remove one of these add-ons to avoid conflicts."
    ).format(conflicting=_CONFLICTING_ADDON_NAME)

    # Speak the warning through NVDA without blocking.
    # Translators: Message spoken by NVDA when a conflicting add-on is detected.
    ui.message(_(
        "Warning: the add-on {conflicting} is also installed and conflicts with "
        "setDescriptionDelay. Please remove one of them."
    ).format(conflicting=_CONFLICTING_ADDON_NAME))

    # Show a non-modal dialog so the user also has a visual reminder.
    # Raise() brings the window to the foreground and SetFocus() moves
    # keyboard focus to it so screen reader users do not have to hunt for it.
    dlg = _ConflictWarningDialog(title, message)
    dlg.Show()
    dlg.Raise()
    dlg.SetFocus()


def getDelay():
    return config.conf['setDescriptionDelay']['delay']


def cancelTimer():
    global characterDescriptionTimer, _timerGeneration
    _timerGeneration += 1  # invalidate any callback already queued in the wx event loop
    if characterDescriptionTimer and characterDescriptionTimer.IsRunning():
        characterDescriptionTimer.Stop()
        characterDescriptionTimer = None


origSpeak = speech.speak
def speak(*args, **kwargs):
    origSpeak(*args, **kwargs)
    if not _suppressCancelInSpeak:
        cancelTimer()

origSpeakSpelling = speech.speakSpelling
def speakSpelling(*args, **kwargs):
    origSpeakSpelling(*args, **kwargs)
    if not _suppressCancelInSpeak:
        cancelTimer()

origCancelSpeech = speech.cancelSpeech
def cancelSpeech():
    origCancelSpeech()
    cancelTimer()


# speech.cancelSpeech() is not always called; for focus changes and object
# navigation NVDA cancels speech directly via SpeechManager.cancel(), bypassing
# our cancelSpeech patch entirely. Patching the method on the class ensures
# the pending description timer is cancelled through every code path.
_origSpeechManagerCancel = None

def _patchedSpeechManagerCancel(self):
    _origSpeechManagerCancel(self)
    cancelTimer()


class _FakeTextInfo():
    def __init__(self, origTextInfo: textInfos.TextInfo):
        self.text = origTextInfo.text
        self.fields = origTextInfo.getTextWithFields({})
        self.obj = getattr(origTextInfo, 'obj', None)

    def getTextWithFields(self, _ = None):
        return self.fields


origSpeakTextInfo = speech.speakTextInfo


def speakTextInfo(*args, **kwargs):
    global characterDescriptionTimer, _suppressCancelInSpeak, _timerGeneration
    info = args[0]
    if (
        config.conf['speech']['delayedCharacterDescriptions']
        and kwargs.get('unit') == textInfos.UNIT_CHARACTER
    ):
        delay = getDelay()
        if delay == 0:
            fakeInfo = _FakeTextInfo(info)
            results = speech.getCharDescListFromText(fakeInfo.text, locale=speech.getCurrentLanguage())
            description = results[0][1] if results else None
            if description:
                _timerGeneration += 1
                speakDelayedDescription(fakeInfo, _timerGeneration)
                return
            config.conf['speech']['delayedCharacterDescriptions'] = False
            _suppressCancelInSpeak = True
            try:
                tmp = origSpeakTextInfo(*args, **kwargs)
            finally:
                _suppressCancelInSpeak = False
            config.conf['speech']['delayedCharacterDescriptions'] = True
            return tmp
        config.conf['speech']['delayedCharacterDescriptions'] = False
        _suppressCancelInSpeak = True
        try:
            tmp = origSpeakTextInfo(*args, **kwargs)
        finally:
            _suppressCancelInSpeak = False
        config.conf['speech']['delayedCharacterDescriptions'] = True
        cancelTimer()
        _timerGeneration += 1
        generation = _timerGeneration
        characterDescriptionTimer = core.callLater(
            delay,
            speakDelayedDescription,
            _FakeTextInfo(info),
            generation,
        )
        return tmp
    # Any non-character read (line, word, sentence, etc.) should cancel a
    # pending description so it does not fire after the new utterance ends.
    cancelTimer()
    return origSpeakTextInfo(*args, **kwargs)


def speakDelayedDescription(info: _FakeTextInfo, generation: int = -1):
    # Guard against stale callbacks that were already queued in the wx event
    # loop when the timer was cancelled (e.g. due to object navigation or a
    # focus change): if the generation counter has moved on, do nothing.
    if generation != -1 and generation != _timerGeneration:
        return
    if info.text.strip() == "":
        return
    curLang = speech.getCurrentLanguage()
    if config.conf['speech']['autoLanguageSwitching']:
        for k in info.fields:
            if isinstance(k, textInfos.FieldCommand) and k.command == "formatChange":
                curLang = k.field.get('language', curLang)
    results = speech.getCharDescListFromText(info.text, locale=curLang)
    if results:
        _, description = results[0]
    else:
        description = None
    if description:
        speech.spellTextInfo(info, useCharacterDescriptions=True)


_origVoiceMakeSettings = None


def _patchedVoiceMakeSettings(self, settingsSizer):
    _origVoiceMakeSettings(self, settingsSizer)

    checkBox = getattr(self, "delayedCharacterDescriptionsCheckBox", None)
    if checkBox is None:
        return

    idx = None
    for i in range(settingsSizer.GetItemCount()):
        item = settingsSizer.GetItem(i)
        if item.GetWindow() == checkBox:
            idx = i
            break
    if idx is None:
        return

    # Translators: Label for the delay spinbox in Voice settings.
    label = wx.StaticText(self, label=_("Description delay (ms, 0=instant):"))
    self._delayMsSpinCtrl = wx.SpinCtrl(
        self, min=0, max=5000,
        initial=getDelay()
    )
    # Translators: Tooltip for the delay spinbox in Voice settings.
    self._delayMsSpinCtrl.SetToolTip(_(
        "Number of milliseconds to wait before announcing the character description. "
        "Set to 0 to announce the description immediately instead of the character."
    ))

    spinSizer = wx.BoxSizer(wx.HORIZONTAL)
    spinSizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
    spinSizer.Add(self._delayMsSpinCtrl, flag=wx.ALIGN_CENTER_VERTICAL)
    settingsSizer.Insert(idx + 1, spinSizer, flag=wx.LEFT, border=10)

    children = list(self.GetChildren())
    try:
        cb_idx = children.index(checkBox)
        next_ctrl = children[cb_idx + 1] if cb_idx + 1 < len(children) else None
        if next_ctrl and next_ctrl not in (label, self._delayMsSpinCtrl):
            self._delayMsSpinCtrl.MoveBeforeInTabOrder(next_ctrl)
            label.MoveBeforeInTabOrder(self._delayMsSpinCtrl)
    except (ValueError, IndexError):
        pass

    self.Layout()

    def _updateVisibility(show):
        label.Show(show)
        self._delayMsSpinCtrl.Show(show)

    _updateVisibility(checkBox.GetValue())

    def _onCheckBox(evt):
        _updateVisibility(evt.IsChecked())
        evt.Skip()

    checkBox.Bind(wx.EVT_CHECKBOX, _onCheckBox)

    origSave = getattr(self.__class__, "onSave", None)
    if origSave is None:
        return

    def _newSave(self):
        origSave(self)
        spinCtrl = getattr(self, "_delayMsSpinCtrl", None)
        if spinCtrl is not None:
            config.conf['setDescriptionDelay']['delay'] = spinCtrl.GetValue()

    self.onSave = types.MethodType(_newSave, self)


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self._patchVoicePanel()
        self._patchSpeechManagerCancel()
        speech.speakTextInfo = speakTextInfo
        speech.speak = speak
        speech.speakSpelling = speakSpelling
        speech.cancelSpeech = cancelSpeech
        # Delay the conflict check slightly so the wx main loop is ready.
        # 2000 ms is enough for NVDA's startup sequence to complete in most cases.
        core.callLater(2000, _checkConflictingAddon)

    def _patchVoicePanel(self):
        global _origVoiceMakeSettings
        if _origVoiceMakeSettings is None:
            _origVoiceMakeSettings = settingsDialogs.VoiceSettingsPanel.makeSettings
            settingsDialogs.VoiceSettingsPanel.makeSettings = _patchedVoiceMakeSettings

    def _patchSpeechManagerCancel(self):
        global _origSpeechManagerCancel
        if _origSpeechManagerCancel is None:
            _origSpeechManagerCancel = speech.manager.SpeechManager.cancel
            speech.manager.SpeechManager.cancel = _patchedSpeechManagerCancel

    def terminate(self):
        global _origVoiceMakeSettings, _origSpeechManagerCancel
        speech.speakTextInfo = origSpeakTextInfo
        speech.speak = origSpeak
        speech.speakSpelling = origSpeakSpelling
        speech.cancelSpeech = origCancelSpeech
        if _origSpeechManagerCancel is not None:
            speech.manager.SpeechManager.cancel = _origSpeechManagerCancel
            _origSpeechManagerCancel = None
        if _origVoiceMakeSettings is not None:
            settingsDialogs.VoiceSettingsPanel.makeSettings = _origVoiceMakeSettings
            _origVoiceMakeSettings = None
        super(GlobalPlugin, self).terminate()