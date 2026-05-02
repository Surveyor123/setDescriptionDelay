# Set Description Delay

NVDA'nın yerleşik gecikmeli karakter açıklaması özelliğini yapılandırılabilir gecikme süresi ve anlık açıklama moduyla genişleten bir NVDA eklentisi.

## Açıklama

NVDA, Konuşma ayarları panelinde "İmleç hareket  ettiğinde imlecin üzerinde bulunan karakteri gecikmeli olarak açıkla" adlı bir onay kutusu içerir. Bu seçenek etkinleştirildiğinde NVDA, imleç bir karakterin üzerine geldiğinde o karakterin fonetik açıklamasını (örneğin "a" için "adana") sabit ve değiştirilemeyen bir gecikmenin ardından seslendirir.

Bu eklenti söz konusu özelliği iki yönde genişletir:

- **Yapılandırılabilir gecikme**: Konuşma ayarları panelinde "İmleç hareket  ettiğinde imlecin üzerinde bulunan karakteri gecikmeli olarak açıkla" onay kutusunun hemen altına, hem görsel sırada hem sekme sırasında, bir sayı kutusu eklenir. Gecikmeyi milisaniye cinsinden ayarlayabilirsiniz (0–5000).
- **Anlık açıklama modu**: Gecikme 0 olarak ayarlandığında karakterin kendisi hiç seslendirilmez; bunun yerine fonetik açıklama anında okunur. Fonetik açıklaması olmayan karakterler (noktalama işaretleri, boşluk vb.) için normal konuşma kuralları geçerli olmaya devam eder; bu sayede Phonetic Punctuation gibi diğer eklentiler doğru çalışmayı sürdürür.

## Gereksinimler

- NVDA 2026.1 veya üzeri

## Kurulum

1. `.nvda-addon` dosyasını indirin.
2. NVDA ile açın (çift tıklayın veya üzerindeyken Enter'a basın).
3. Kurulum yönergelerini izleyin ve istendiğinde NVDA'yı yeniden başlatın.

> **Not:** Bilgisayarınızda **EnhancedPhoneticReading** eklentisi kuruluysa, eklenti kurulumunun ardından bir uyarı iletişim kutusu açılır. Her iki eklenti de aynı iç konuşma işlevlerini değiştirdiğinden birlikte kullanımları öngörülemeyen davranışlara (çift konuşma, kaçırılan karakter açıklamaları vb.) yol açabilir. Çakışmayı önlemek için eklentilerden birini kaldırmanız önerilir.

## Kullanım

1. NVDA Ayarları'nı açın (NVDA+N → Tercihler → Ayarlar).
2. **Konuşma** kategorisine gidin.
3. Henüz işaretli değilse **"İmleç hareket  ettiğinde imlecin üzerinde bulunan karakteri gecikmeli olarak açıkla"** onay kutusunu işaretleyin.
4. Onay kutusunun hemen altında, hem görsel sırada hem sekme sırasında **"Açıklama gecikmesi (ms, 0=anlık)"** sayı kutusu belirir.
5. Tercih ettiğiniz gecikmeyi ayarlayın:
   - **0** — Fonetik açıklamayı karakterin kendisi yerine anında seslendirir.
   - **1–5000** — Önce karakteri seslendirir, ardından belirtilen milisaniye kadar bekleyip fonetik açıklamayı okur.
6. Kaydetmek için Tamam veya Uygula'ya tıklayın.

## Notlar

- Sayı kutusu, "Gecikmeli karakter açıklamaları" onay kutusu işaretsizken gizlenir.
- Eklenti, `speech.speakTextInfo` işlevini değiştiren diğer eklentilerle (BrowserNav, Phonetic Punctuation vb.) uyumlu çalışır. `_FakeTextInfo` nesnesi `obj` özniteliğini açığa çıkararak uyumluluğu korur.
- Gecikme değeri tüm sentezleyici ve sesler için ortaktır. Farklı sentezleyicilerde farklı değerler kullanmak istiyorsanız NVDA konfigürasyon  profillerinden yararlanabilirsiniz.