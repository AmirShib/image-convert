import cv2 
import numpy as np
from pydantic import BaseModel 
from abc import ABC, abstractmethod
from typing import Tuple

class BaseConverter(ABC):
    
    @abstractmethod
    def convert(self, input_image: dict) -> dict:
        raise NotImplementedError("Subclasses must implement this method")


class CartoonConverter(BaseConverter):
    
    def convert(self, input_image: dict) -> dict:
        url = input_image['url']
        img = cv2.imread(url)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(img, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        return {"img": cartoon}
    

class DrawingConverter(BaseConverter):
    
    def __init__(
        self,
        blur_simga: int = 5,
        ksize: Tuple[int, int] = (0, 0),
        sharpen_value: int = None,
        kernel: np.ndarray = None,
        ) -> None:
        
        self.blur_simga = blur_simga
        self.ksize = ksize
        self.sharpen_value = sharpen_value
        self.kernel = np.array([[0, -1, 0], [-1, sharpen_value,-1], [0, -1, 0]]) if kernel == None else kernel
    
    def convert(self, input_image: dict) -> dict:
        url = input_image['url']
        img = cv2.imread(url)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        inverted_img = 255 - gray

        blur_img = cv2.GaussianBlur(inverted_img, ksize=self.ksize, sigmaX=self.blur_simga)
        final_img = self._blend(blur_img, gray)

        sharpened_image = self._sharpen(final_img)

        return {"img": sharpened_image}
        
    def _blend(self, front: np.ndarray, back: np.ndarray) -> np.ndarray:
        result = back*255.0 / (255.0-front) 
        result[result>255] = 255
        result[back==255] = 255
        return result.astype('uint8')
        
    def _sharpen(self, image: np.ndarray) -> np.ndarray:
        """Sharpen image by defined kernel size
        Args:
            image: (np.ndarray) - image to be sharpened

        Returns:
            image: (np.ndarray) - sharpened image
        """
        if self.sharpen_value is not None and isinstance(self.sharpen_value, int):
            inverted = 255 - image
            return 255 - cv2.filter2D(src=inverted, ddepth=-1, kernel=self.kernel)

        return image


class AsciConverter(BaseConverter):
        
        def __init__(self, scale: int = 1) -> None:
            self.scale = scale
        
        def convert(self, input_image: dict) -> dict:
            url = input_image['url']
            img = cv2.imread(url, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, (int(img.shape[1] * self.scale), int(img.shape[0] * self.scale)))
            ascii_str = ''
            for row in img:
                for pixel in row:
                    ascii_str += self._get_ascii_char(pixel)
                ascii_str += '\n'
            return {"img": ascii_str}
        
        def _get_ascii_char(self, pixel: int, ascii_chars: str = '@JD%#*P$+=-:. ') -> str:
            """
            Converts a pixel intensity to an ASCII character based on the intensity.

            Parameters:
                pixel (int): The pixel intensity, must be between 0 and 255.
                ascii_chars (str): A string of characters used for ASCII art, ordered from darkest to lightest.

            Returns:
                str: The ASCII character corresponding to the pixel intensity.
            """
            pixel = max(0, min(255, pixel))  # Ensure pixel is within [0, 255]
            scale_factor = 255 / (len(ascii_chars) - 1)
            return ascii_chars[int(pixel / scale_factor)]
