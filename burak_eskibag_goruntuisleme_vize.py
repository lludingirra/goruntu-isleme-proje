import cv2
import numpy as np
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MARGIN = 10  # Görüntüdeki metin ile elin bounding box'ı arasındaki boşluk (piksel)
FONT_SIZE = 1  # Görüntüdeki metin font boyutu
FONT_THICKNESS = 1  # Görüntüdeki metin font kalınlığı
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # Görüntüdeki elin sağ/sol bilgisinin rengi (canlı yeşil)

# El landmark'larının belirli bir indeksine göre koordinatları (x, y) piksel cinsinden alır.
# landmarks: El landmark'larının listesi
# indeks: İstenen landmark'ın indeksi (örneğin, işaret parmağı ucu için 8)
# h: Görüntü yüksekliği
# w: Görüntü genişliği
def koordinat_getir(landmarks, indeks, h, w):
    landmark = landmarks[indeks]
    return int(landmark.x * w), int(landmark.y * h)

# Algılanan el landmark'larını görüntü üzerine çizer.
# rgb_image: İşlenecek RGB formatındaki görüntü
# detection_result: El landmark tespiti sonuçları
def draw_landmarks_on_image(rgb_image, detection_result):
    # Algılanan her el için landmark listesini alır.
    hand_landmarks_list = detection_result.hand_landmarks
    # Algılanan her elin sağ mı sol mu olduğunu gösteren listeyi alır.
    handedness_list = detection_result.handedness
    # Orjinal görüntünün bir kopyasını oluşturur üzerine çizim yapmak için.
    annotated_image = np.copy(rgb_image)
    # Görüntü boyutlarını (yükseklik, genişlik, kanal sayısı) alır.
    h, w, c = annotated_image.shape

    # Algılanan eller arasında döngü kurar.
    for idx in range(len(hand_landmarks_list)):
        # Şu anki elin landmark noktalarını alır.
        hand_landmarks = hand_landmarks_list[idx]
        # İşaret parmağı ucunun koordinatlarını alır (indeks 8).
        x1, y1 = koordinat_getir(hand_landmarks, 8, h, w)
        # Orta parmak ucunun koordinatlarını alır (indeks 12).
        x2, y2 = koordinat_getir(hand_landmarks, 12, h, w)
        renk = (255, 255, 0)  # Çizim rengi (cyan)
        # İşaret parmağı ucuna bir daire çizer.
        annotated_image = cv2.circle(annotated_image, (x1, y1), 9, renk, 5)
        # Baş parmak ucuna bir daire çizer.
        annotated_image = cv2.circle(annotated_image, (x2, y2), 9, renk, 5)
        # İşaret ve baş parmak uçları arasına bir çizgi çizer.
        annotated_image = cv2.line(annotated_image, (x1, y1), (x2, y2), renk, 5)
        # İki parmak arasındaki orta noktanın koordinatlarını hesaplar.
        xort = (x1 + x2) // 2
        yort = (y1 + y2) // 2
        # Orta noktaya bir daire çizer.
        annotated_image = cv2.circle(annotated_image, (xort, yort), 9, (0, 255, 255), 5)  # Sarı
        # İki parmak arasındaki mesafeyi hesaplar.
        uzaklik = int(np.hypot(x2 - x1, y2 - y1))
        # Mesafeyi görüntü üzerinde orta noktanın yanına yazar.
        annotated_image = cv2.putText(annotated_image, str(uzaklik), (xort, yort), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 4)  # Mavi
        # Şu anki elin sağ mı sol mu bilgisini alır.
        handedness = handedness_list[idx]

        # El landmark'larını çizmek için bir NormalizedLandmarkList proto nesnesi oluşturur.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])

        # MediaPipe'in çizim yardımcı fonksiyonunu kullanarak el landmark'larını ve bağlantılarını çizer.
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

        # Algılanan elin bounding box'ının sol üst köşesinin koordinatlarını hesaplar.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Elin sağ mı sol mu olduğunu görüntü üzerine yazar.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image

# Bir HandLandmarker nesnesi oluşturur. Bu nesne el landmark tespiti için kullanılır.
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options,
                                           num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

# Kamera yakalamayı başlatır (varsayılan kamera aygıtı 0).
cap = cv2.VideoCapture(0)
# Yakalanan karelerin genişliğini 1280 piksele ayarlar.
cap.set(3, 1280)
# Yakalanan karelerin yüksekliğini 720 piksele ayarlar.
cap.set(4, 720)

# Oyun elementlerinin renk tanımları.
color_rect = (210, 204, 5)  # Dikdörtgen rengi (açık mavi)
color_circle = (0, 0, 255)  # Daire rengi (kırmızı)
color_finish = (0, 255, 0)  # Bitiş noktası rengi (yeşil)

# Sürüklenip bırakılabilir dikdörtgen sınıfı.
class DragRect:
    # Dikdörtgenin merkez pozisyonunu ve boyutunu başlatır.
    def __init__(self, posCenter, size=[100, 100]):
        self.posCenter = posCenter
        self.size = size

    # Bir dairenin (merkez ve yarıçapı ile tanımlanır) bu dikdörtgenle çarpışıp çarpışmadığını kontrol eder.
    def check_collision(self, circle_center, radius):
        cx, cy = self.posCenter
        w, h = self.size
        # Dairenin merkezine en yakın dikdörtgen üzerindeki noktayı bulur.
        closest_x = max(cx - w // 2, min(circle_center[0], cx + w // 2))
        closest_y = max(cy - h // 2, min(circle_center[1], cy + h // 2))
        # En yakın nokta ile daire merkezi arasındaki mesafeyi hesaplar.
        distance = np.hypot(closest_x - circle_center[0], closest_y - circle_center[1])
        # Mesafe yarıçaptan küçükse çarpışma vardır.
        return distance < radius

# Sürüklenip bırakılabilir daire sınıfı.
class DragCircle:
    # Dairenin başlangıç pozisyonunu, merkez pozisyonunu ve yarıçapını başlatır.
    def __init__(self, posCenter, radius=30):
        self.start_pos = posCenter
        self.posCenter = posCenter
        self.radius = radius
        self.grabbed = False  # Dairenin şu anda sürüklenip bırakılmadığını gösteren bayrak

    # Dairenin pozisyonunu imlecin (parmak ucu) pozisyonuna göre günceller eğer yakalanmışsa.
    def update(self, cursor):
        if self.grabbed:
            self.posCenter = cursor[:2]

# Oyunu başlangıç durumuna sıfırlar.
def reset_game():
    global game_over, game_won, circle
    game_over = False
    game_won = False
    circle.posCenter = circle.start_pos  # Daireyi başlangıç pozisyonuna geri alır.
    circle.grabbed = False  # Dairenin yakalanma durumunu da sıfırlar.

# Dikdörtgenlerin başlangıç pozisyonlarının listesi.
rect_positions = [
    (200, 200), (400, 200), (600, 200), (800, 200), (1000, 200),
    (200, 400), (400, 400), (800, 400), (1000, 400),
    (200, 600), (600, 600), (1000, 600)
]

# Belirtilen pozisyonlara göre DragRect nesneleri oluşturur.
rectList = [DragRect(pos) for pos in rect_positions]

# Sürüklenip bırakılabilir daire nesnesi oluşturur.
circle = DragCircle([640, 360])

# Bitiş noktasının pozisyonu ve yarıçapı.
finish_pos = (1100, 100)
finish_radius = 40

# Oyunun durumunu gösteren bayraklar.
game_over = False
game_won = False

# Ana oyun döngüsü.
while True:
    # Kameradan bir kare okur.
    success, img = cap.read()
    # Kareyi yatay olarak aynalar (daha doğal bir kullanıcı deneyimi için).
    img = cv2.flip(img, 1)
    # Görüntü boyutlarını alır.
    h, w, _ = img.shape

    # Kare okuma başarısız olursa döngüden çıkar.
    if not success:
        print("Unable to capture camera image!")
        break

    # Kameradan alınan BGR formatındaki kareyi MediaPipe'in işleyebileceği RGB formatına dönüştürür.
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # MediaPipe ile el landmark tespiti yapar.
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
    detection_result = detector.detect(mp_image)

    # El landmark'ları algılanmışsa ve oyun henüz bitmemişse/kazanılmamışsa.
    if detection_result.hand_landmarks : 
        img = draw_landmarks_on_image(img, detection_result)
        # Algılanan el landmark'larının listesini alır.
        if not game_over and not game_won:
            # Algılanan el landmark'larının listesini alır.
            hand_landmarks_list = detection_result.hand_landmarks
        # En az bir el algılanmışsa.
            if len(hand_landmarks_list) >= 1:
                # İlk algılanan elin landmark'larını alır.
                hand_landmarks = hand_landmarks_list[0]
                # Yeterli sayıda landmark varsa (işaret ve orta parmak uçları için).
                if len(hand_landmarks) > 12:
                    # İşaret parmağı ucunun koordinatlarını alır (indeks 8).
                    x1, y1 = koordinat_getir(hand_landmarks, 8, h, w)
                    # Orta parmak ucunun koordinatlarını alır (indeks 12).
                    x2, y2 = koordinat_getir(hand_landmarks, 12, h, w)
    
                    # İki parmak arasındaki mesafeyi hesaplar.
                    distance = int(np.hypot(x2 - x1, y2 - y1))
    
                    # Eğer parmaklar yeterince yakınsa kırmızı daire sürüklenir.
                    if distance < 60:
                        # İmleç pozisyonunu işaret parmağı ucuna ayarlar.
                        cursor = (x1, y1)
                        # İmleç dairenin içindeyse daireyi yakalar.
                        if np.hypot(cursor[0] - circle.posCenter[0], cursor[1] - circle.posCenter[1]) < circle.radius:
                            circle.grabbed = True
                    # Parmaklar ayrıldığında dairenin yakalanma durumunu sıfırlar.
                    else:
                        circle.grabbed = False
    
                    # Daire yakalanmışsa pozisyonunu imlecin pozisyonuna göre günceller.
                    if circle.grabbed:
                        circle.update(cursor)

    # Oyun elementlerinin (dikdörtgenler) çizileceği boş bir görüntü oluşturur.
    imgNew = np.zeros_like(img, np.uint8)

    # Dikdörtgen listesindeki her dikdörtgeni çizer.
    for rect in rectList:
        cx, cy = rect.posCenter
        ww, hh = rect.size
        cv2.rectangle(imgNew, (cx - ww // 2, cy - hh // 2),
                      (cx + ww // 2, cy + hh // 2), color_rect, cv2.FILLED)

    # Sürüklenip bırakılabilir daireyi çizer.
    cv2.circle(img, circle.posCenter, circle.radius, color_circle, cv2.FILLED)

    # Bitiş noktasını çizer.
    cv2.circle(img, finish_pos, finish_radius, color_finish, cv2.FILLED)

    # Her dikdörtgen için daire ile çarpışma olup olmadığını kontrol eder.
    for rect in rectList:
        # Çarpışma kontrolünde math.sqrt yerine np.hypot kullanılıyor.
        distance = np.hypot(rect.posCenter[0] - circle.posCenter[0], rect.posCenter[1] - circle.posCenter[1])
        combined_radius = (rect.size[0] // 2 + rect.size[1] // 2) / 2 + circle.radius # Basit bir yaklaşık çarpışma kontrolü
        if distance < combined_radius:
            game_over = True  # Çarpışma olursa oyunu bitirir.

    # Dairenin bitiş noktasına ulaşıp ulaşmadığını kontrol eder.
    if np.hypot(circle.posCenter[0] - finish_pos[0], circle.posCenter[1] - finish_pos[1]) < (circle.radius + finish_radius):
        game_won = True  # Bitiş noktasına ulaşılırsa oyunu kazanır.

    # Oyun bittiyse "GAME OVER" mesajını görüntüler.
    if game_over:
        cv2.putText(imgNew, "GAME OVER! Press 'R' to Restart", (350, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 5)
    # Oyun kazanıldıysa "YOU WIN!" mesajını görüntüler.
    elif game_won:
        cv2.putText(imgNew, "YOU WIN! Press 'R' to Restart", (400, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 5)

    # Orjinal kamera görüntüsü ile oyun elementlerinin çizildiği görüntüyü birleştirir (şeffaflık efekti ile).
    out = img.copy()
    alpha = 0.1  # Şeffaflık katsayısı
    mask = imgNew.astype(bool)  # Oyun elementlerinin olduğu yerleri maskeler.
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]

    # Birleştirilmiş görüntüyü gösterir.
    cv2.imshow("IMG", out)

    # Klavyeden bir tuşa basılmasını bekler (1 milisaniye).
    key = cv2.waitKey(1)
    # 'q' veya 'Q' tuşuna basılırsa döngüden çıkar (programı sonlandırır).
    
    if key == ord('q') or key == ord('Q'):
        break
    # 'r' veya 'R' tuşuna basılırsa oyunu yeniden başlatır.
    elif key == ord('r') or key == ord('R'):
        reset_game()

# Kamera yakalamayı serbest bırakır.
cap.release()
# Tüm OpenCV pencerelerini kapatır.
cv2.destroyAllWindows()