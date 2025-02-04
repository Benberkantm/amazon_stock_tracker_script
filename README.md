# amazon_stock_tracker_script
Amazon Stok Takip Sistemi

Bu program, Amazon ürünlerinin stok durumunu belirli aralıklarla kontrol eder ve sonuçları Excel dosyasına kaydeder. Stokta olmayan ürünler için rapor oluşturur.

Gereksinimler:

Python 3.7+

Google Chrome

Konsola aşağıdaki gibi yazıp Python kütüphanelerini kurun:

pip install pandas requests beautifulsoup4 selenium webdriver-manager
Kurulum Adımları:

Kodu İndirin:

Python betiğini bilgisayarınıza kaydedin (örneğin: amazon_stock_monitor.py).

Chrome Cookie Ayarları:

load_cookies_from_chrome() fonksiyonundaki Chrome profil yolunu kendi sisteminize göre düzenleyin:

options.add_argument("user-data-dir=C:/Users/<KULLANICI_ADI>/AppData/Local/Google/Chrome/User Data")

Ürün Listesi Hazırlayın:

amazon_products.xlsx adında bir Excel dosyası oluşturun.(Oluşturmasanız da ilk çalıştırmanın ardından kendisi oluşturacaktır)

Sütun başlıkları: URL, Product Name, In Stock, Last Checked.

Takip etmek istediğiniz ürünlerin Amazon URL'lerini "URL" sütununa ekleyin.

Programı Çalıştırın:

Terminali açıp betiği çalıştırın:
python amazon_stock_monitor.py


Çalışma Mantığı:

Program her 1 saatte bir (varsayılan) tüm URL'leri kontrol eder.

Stok durumu In Stock sütununda True/False olarak güncellenir.

Stokta olmayan ürünler out_of_stock_<TARİH>.xlsx dosyasına kaydedilir.

Önemli Notlar:

İlk çalıştırmada Chrome oturumunuz açıksa, Amazon giriş yapılmış halde cookie'ler kullanılır.

Programı kapatıp tekrar açarsanız, önceki veriler Excel'den okunur.

Amazon'un bot engellemesine karşı rastgele gecikmeler eklenmiştir. Bu süreleri değiştirmeyin.

Sorun Giderme:

"ChromeDriver Bulunamadı" Hatası: Chrome'un en son sürümünü yükleyin.

Cookie Hatası: Chrome'da Amazon'a manuel giriş yapıp tekrar deneyin.

Excel Dosyası Açık: Dosyayı kapatıp programı yeniden başlatın.
 amazon_stock_tracker_script
