import cv2 
import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple

class BaseConverter(ABC):
    
    @abstractmethod
    def convert(self, input_image):
        raise NotImplementedError("Subclasses must implement this method")


class CartoonConverter(BaseConverter):
    
    def convert(self, input_image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        color = cv2.bilateralFilter(input_image, 9, 300, 300)
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        return cartoon
    

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
    
    def convert(self, input_image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        
        inverted_img = 255 - gray

        blur_img = cv2.GaussianBlur(inverted_img, ksize=self.ksize, sigmaX=self.blur_simga)
        final_img = self._blend(blur_img, gray)

        sharpened_image = self._sharpen(final_img)

        return sharpened_image
        
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
                
    def __init__(self, size: Tuple[int,int] = (100, 50), ascii_chars: str = "@$&%#*+=-:!,.") -> None:
        self.size = size
        self.ascii_chars = ascii_chars
        self.length = len(self.ascii_chars) - 1
        # Adjust scale factor to map pixel values to the index of ascii_chars more accurately
        self.scale_factor = 255 / self.length 
        
    def convert(self, input_image: np.ndarray) -> str:
        img = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        adjusted_size = (self.size[0], int(self.size[1] * (2/1)))
        img = cv2.resize(img, adjusted_size, interpolation=cv2.INTER_AREA)
        img = img = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
        ascii_str = ''

        # Process the image by 2x1 blocks to maintain the aspect ratio
        for y in range(0, img.shape[0], 2):  # Adjust block height considering character aspect ratio
            for x in range(0, img.shape[1], 1):
                # Calculate the average brightness of the block
                block_avg = np.mean(img[y:y+2, x:x+1])
                ascii_index = int(block_avg / self.scale_factor)
                ascii_str += self.ascii_chars[ascii_index]
            ascii_str += '\n'
        return ascii_str
        
    def _get_ascii_char(self, pixel: int) -> str:
        """
        Converts a pixel intensity to an ASCII character based on the intensity
        Parameters:
            pixel (int): The pixel intensity, must be between 0 and 255
        Returns:
            str: The ASCII character corresponding to the pixel intensity.
        """
        #pixel = max(0, min(255, pixel))  # Ensure pixel is within [0, 255]
        return self.ascii_chars[min(int(pixel / self.scale_factor),self.length)]
            
       

class Converter_factory:
    def __init__(self,converter_type: str) -> None:
        self.converter_type = converter_type
        
    def __call__(self) -> BaseConverter:
        if self.converter_type == "cartoon":
            return CartoonConverter()
        elif self.converter_type == "drawing":
            return DrawingConverter()
        elif self.converter_type == "ascii":
            return AsciConverter()
        else:
            raise ValueError("Invalid converter type")