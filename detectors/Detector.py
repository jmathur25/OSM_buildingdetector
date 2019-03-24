from .Rectangle import Rectangle
from .SimpleDetect import SimpleDetect

# interface for managing all the detectors
# all detectors should implement:
class Detector:
    id_to_rect = {}
    id_to_strategy = {}
    strategy_to_id = {}

    def __init__(self, detection_strategy, image, lat, long, zoom, threshold, merge_mode):
        self.strategy = detection_strategy
        self.detector = None
        self.merge_mode = merge_mode
        if (self.strategy == 'simple_detect'):
            self.detector = SimpleDetect(image, lat, long, zoom, threshold)
    
    def detect_building(self):
        corners = self.detector.detect_building()
        new_rect = Rectangle(corners)

        if self.merge_mode:
            for rect_id in Detector.strategy_to_id[self.strategy]:
                possible_rect = Detector.id_to_rect[rect_id].merge_with(new_rect)
                if possible_rect is not None:
                    print('found match!')
                    new_rect = possible_rect
                    break

        # updates id_to_rect, id_to_strategy, strategy_to_id with the current rectangle
        Detector.id_to_rect[new_rect.get_id()] = new_rect
        Detector.id_to_strategy[new_rect.get_id()] = self.strategy
        if self.strategy in Detector.strategy_to_id:
            Detector.strategy_to_id[self.strategy].append(new_rect.get_id())
        else:
            Detector.strategy_to_id[self.strategy] = [new_rect.get_id()]

        return new_rect.get_id(), new_rect.get_points(), [] # new_rect.get_deleted_rects()

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

    