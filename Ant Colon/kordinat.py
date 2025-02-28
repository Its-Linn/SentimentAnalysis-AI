import cv2
import numpy as np
import pandas as pd

class CoordinatePicker:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path)
        self.coordinates = []
        self.window_name = "Buat orang mager"
        self.current_point = 0
        self.max_points = 30
        
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.current_point < self.max_points:
                # Simpen koordinat
                self.coordinates.append((x, y))
                self.current_point += 1
                
                # Gambar titik
                cv2.circle(self.image, (x, y), 5, (0, 0, 255), -1)
                cv2.putText(self.image, f"P{self.current_point}({x},{y})", 
                          (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.5, (0, 0, 255), 1)
                
                print(f"Point {self.current_point}: ({x}, {y})")
                
                # refresh tampilan
                cv2.imshow(self.window_name, self.image)
                
                if self.current_point == self.max_points:
                    print("\nUdah 30 Titik")
                    self.save_coordinates()
    
    def save_coordinates(self):
        # Simpen koordinat ke csv
        df = pd.DataFrame(self.coordinates, columns=['x', 'y'])
        df.index = df.index + 1  # Mulai dari 1 bukan 0
        df.to_csv('coordinates.csv')
        print("\nKoordinat disimpan ke 'coordinates.csv'")
    
    def start(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        while True:
            cv2.imshow(self.window_name, self.image)
            key = cv2.waitKey(1) & 0xFF
            
            # q buat quit
            if key == ord('q'):
                break
            # u buat undo
            elif key == ord('u') and self.current_point > 0:
                self.current_point -= 1
                self.coordinates.pop()
                # load gambar map
                self.image = cv2.imread(image_path)
                # nampilin titik
                for i, (x, y) in enumerate(self.coordinates):
                    cv2.circle(self.image, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(self.image, f"P{i+1}({x},{y})", 
                              (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (0, 0, 255), 1)
                cv2.imshow(self.window_name, self.image)
        
        cv2.destroyAllWindows()

'''
Cara Pake untuk mas kamil:
1. Ganti image_path sama lokasi map kamu
2. run program
3. klik 30 tempat nanti otomatis ke titik
4. pencet u kalo mau undo dan q kalo udah beres
5. jangan lupa catat urutan nama tempat yang di klik
6. nanti kordinatnya ada di file coordinates.csv'''


image_path = "Ant Colon\maps.png"
picker = CoordinatePicker(image_path)
picker.start()