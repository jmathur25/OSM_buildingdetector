from .Rectangle import Rectangle
from .SimpleDetect import SimpleDetect

# interface for managing all the detectors
# old wrapper class for a variety of detectors, of which only SimpleDetect is used now
class Detector:
    id_to_rect = {}
    def __init__(self, image, lat, lng, zoom, threshold=50):
        self.detector = SimpleDetect(image, lat, lng, zoom, threshold)
    
    def detect_building(self):
        corners = self.detector.detect_building()
        new_rect = Rectangle(corners)

        # updates id_to_rect, id_to_strategy, strategy_to_id with the current rectangle
        Detector.id_to_rect[new_rect.get_id()] = new_rect
        return new_rect.get_id(), new_rect.get_points()

    @staticmethod
    def reset():
        Detector.id_to_rect = {}
        Detector.id_to_strategy = {}
        Detector.strategy_to_id = {}

    @staticmethod
    def delete_rect(rect_id):
        del Detector.id_to_rect[rect_id]
        # finds the strategy of the rect_id and removes it from the strategy list
        Detector.strategy_to_id[Detector.id_to_strategy[rect_id]].remove(rect_id)
        del Detector.id_to_strategy[rect_id]

    