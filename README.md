# Pinch & Dash İnteraktif Oyun

Bu proje, kameradan alınan görüntüdeki elin işaret ve baş parmakları arasındaki mesafeyi kullanarak basit bir interaktif oyunu kontrol etmeyi amaçlar. Kullanıcı, parmak mesafesini değiştirerek ekrandaki kırmızı daireyi hareket ettirebilir ve mavi engellerden kaçınarak yeşil bitiş noktasına ulaşmaya çalışır.

## Genel Bakış

Bu oyun, gerçek zamanlı el takibi için MediaPipe kütüphanesini kullanır. Kameradan alınan görüntüdeki elin işaret ve baş parmak uçları arasındaki mesafe hesaplanarak, ekrandaki kırmızı dairenin etkileşimi sağlanır. Amaç, el hareketleriyle basit bir kontrol mekanizması oluşturmaktır.

## Kurulum

Bu projeyi çalıştırmak için aşağıdaki adımları izleyin:

1.  **Gereksinimleri Kontrol Edin:** Sisteminizde Python 3.x'in kurulu olduğundan emin olun. Ayrıca, aşağıdaki Python kütüphanelerinin de kurulu olması gerekmektedir:
    -   OpenCV (`opencv-python`)
    -   NumPy (`numpy`)
    -   MediaPipe (`mediapipe`)
    -   MediaPipe Tasks (`mediapipe-tasks`)

2.  **Bağımlılıkları Yükleyin:** Proje klasörünüzde bir terminal (Komut İstemi veya Bash) açın ve aşağıdaki komutu çalıştırarak gerekli kütüphaneleri yükleyin:

    ```bash
    pip install opencv-python numpy mediapipe mediapipe-tasks
    ```

3.  **MediaPipe Model Dosyasını Edinin:** Proje, el landmark tespiti için `hand_landmarker.task` dosyasına ihtiyaç duyar. Bu dosyayı [MediaPipe Tasks documentation](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models) adresinden indirebilir ve proje ana dizininize kaydedin.

## Çalıştırma

Oyunu başlatmak için aşağıdaki adımları uygulayın:

1.  **Terminalde Çalıştırın:** Proje ana dizininizde bir terminal açın ve ana oyun dosyasını (genellikle `.py` uzantılıdır, örneğin `oyun.py` veya bu dosyanın adı neyse) aşağıdaki komutla çalıştırın:

    ```bash
    python <ana_oyun_dosyası>.py
    ```

    `<ana_oyun_dosyası>.py` yerine projenizin ana Python dosyasının adını yazın (örneğin `parmak_oyun.py`).

2.  **Kamera Erişimine İzin Verin:** Uygulama çalıştırıldığında web kameranıza erişim isteyecektir. Lütfen erişime izin verin.

3.  **Oyun Penceresini Görüntüleyin:** Başarıyla çalıştırıldığında, oyunun görsel arayüzünü içeren bir pencere açılacaktır.

## Nasıl Oynanır

Oyunda amacınız, elinizin işaret ve baş parmakları arasındaki mesafeyi kullanarak kırmızı daireyi kontrol etmek ve mavi dikdörtgen engellere çarpmadan yeşil bitiş noktasına ulaşmaktır.

-   **Kontrol Mekanizması:**
    -   **Yakala ve Sürükle:** İşaret ve baş parmaklarınızı birbirine yaklaştırdığınızda (parmaklarınız arasındaki mesafe belirli bir eşiğin altına düştüğünde), eğer kırmızı dairenin üzerindeyse, daireyi "yakalayabilirsiniz". Parmağınızı hareket ettirerek yakaladığınız daireyi ekran üzerinde sürükleyebilirsiniz.
    -   **Bırak:** Parmağınızı birbirinden uzaklaştırdığınızda (parmaklarınız arasındaki mesafe belirli bir eşiğin üzerine çıktığında), daireyi bırakırsınız.

-   **Oyun Elemanları:**
    -   **Kırmızı Daire:** Kullanıcının parmak mesafesiyle kontrol ettiği etkileşimli nesne.
    -   **Mavi Dikdörtgenler:** Oyuncunun çarpmaması gereken engeller. Bu engellere çarpmak oyunu kaybetmenize neden olur.
    -   **Yeşil Daire:** Oyuncunun ulaşması gereken bitiş noktası. Kırmızı daireyi bu noktaya ulaştırmak oyunu kazanmanızı sağlar.

-   **Oyun Kontrolleri:**
    -   **Yeniden Başlatma:** Oyun bittiğinde (kaybettiğinizde veya kazandığınızda), klavyenizden `R` veya `r` tuşuna basarak oyunu yeniden başlatabilirsiniz.
    -   **Çıkış:** Oyundan çıkmak için klavyenizden `Q` veya `q` tuşuna basın.

