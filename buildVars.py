# Build customizations
# Change this file instead of sconstruct or manifest files, whenever possible.

from site_scons.site_tools.NVDATool.typings import AddonInfo, BrailleTables, SymbolDictionaries
from site_scons.site_tools.NVDATool.utils import _

# Add-on information variables
addon_info = AddonInfo(
	# add-on Name/identifier, internal for NVDA
	addon_name="setDescriptionDelay",
	
	# Add-on summary/title, usually the user visible name of the add-on
	# Translators: Summary/title for this add-on
	addon_summary=_("Set Character Description Delay"),
	
	# Add-on description
	# Translators: Long description to be shown for this add-on
	addon_description=_("""This add-on improves NVDA's delayed character description feature:
	Allows you to configure the announcement delay in milliseconds, offering more flexibility than the built-in option.
	When the delay is set to 0, the character description is announced immediately instead of the character itself.
	The add-on is controlled entirely through NVDA's existing \"Delayed descriptions for characters on cursor movement" checkbox in Voice settings."""),
	
	# version
	addon_version="2026.1.1",
	
	# Brief changelog for this version
	# Translators: what's new content for the add-on version
	addon_changelog=_("""
Fixed: Character descriptions no longer bleed into subsequent speech after switching away from character-by-character navigation. Previously, if you moved to a different object or application while a description was pending, the description would still be announced after the new object's name. This happened because NVDA cancels speech internally via SpeechManager.cancel() rather than speech.cancelSpeech() during focus and object navigation events, bypassing the add-on's timer cancellation entirely. The fix patches SpeechManager.cancel() directly and adds a generation counter so that any callback already queued in the wx event loop when cancellation occurs is silently discarded.
"""),
	
	# Author(s)
	addon_author="Çağrı Doğan <cagrid@hotmail.com>",
	
	# URL for the add-on documentation support
	addon_url="https://github.com/Surveyor123/setDescriptionDelay",
	
	# URL for the add-on repository where the source code can be found
	addon_sourceURL="https://github.com/Surveyor123/setDescriptionDelay",
	
	# Documentation file name
	addon_docFileName="readme.html",
	
	# Minimum NVDA version supported
	addon_minimumNVDAVersion="2026.1.0",
	
	# Last NVDA version supported/tested
	addon_lastTestedNVDAVersion="2026.1.0",
	
	# Add-on update channel (None denotes stable releases)
	addon_updateChannel=None,
	
	# Add-on license
	addon_license="GPL-2.0",
	addon_licenseURL=None,
)

# Define the python files that are the sources of your add-on.
# We point to the specific directory where your code lives.
pythonSources: list[str] = ["addon/globalPlugins/setDescriptionDelay/*.py"]

# Files that contain strings for translation. Usually your python sources
i18nSources: list[str] = pythonSources + ["buildVars.py"]

# Files that will be ignored when building the nvda-addon file
excludedFiles: list[str] = []

# Base language for the NVDA add-on
# Since your code strings (e.g. _("Table")) are in English, we keep this as "en".
baseLanguage: str = "en"

# Markdown extensions for add-on documentation
markdownExtensions: list[str] = []

# Custom braille translation tables
brailleTables: BrailleTables = {}

# Custom speech symbol dictionaries
symbolDictionaries: SymbolDictionaries = {}