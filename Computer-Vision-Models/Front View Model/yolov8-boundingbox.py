import cv2
import argparse

from ultralytics import YOLO
import ultralytics
import supervision as sv
import numpy as np

import os

ZONE_POLYGON = np.array([
    [0, 0],
    [0.5, 0],
    [0.5, 1],
    [0, 1]
])

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution", 
        default=[1280, 720], 
        nargs=2, 
        type=int
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("best.pt")

    file_create = open("/home/joe/Test/readme.txt", "w")
    file_create.write("Ready")
    file_create.close()

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    #zone_polygon = (ZONE_POLYGON * np.array(args.webcam_resolution)).astype(int)
    #zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=tuple(args.webcam_resolution))
    # zone_annotator = sv.PolygonZoneAnnotator(
    #     zone=zone, 
    #     color=sv.Color.red(),
    #     thickness=2,
    #     text_thickness=4,
    #     text_scale=2
    # )

    while True:
        ret, frame = cap.read()

        result = model(frame, agnostic_nms=True)[0]

        # result = model.predict(source="0",show=True)
        # print(result)

        detections = sv.Detections.from_yolov8(result)

        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]
        frame = box_annotator.annotate(
            scene=frame, 
            detections=detections, 
            labels=labels
        )
        #Save any errors over a set Limit
        #Get the two varables confideince and the label ID
        conf = [
            f"{confidence:0.2f}"
            for _, confidence, _, _
            in detections
        ]
        ID = [
            f"{model.model.names[class_id]}"
            for _, _, class_id, _
            in detections
        ]
        #If a error is detected see which error and then the confidience of it. Only save the error if its over the set threshold
        #Currently using hardcoded values from testing due to biasing in the model. 
        #TODO: Change the If-else to dictionary with key check
        if len(conf) > 0:
            f = open("/home/joe/Test/readme.txt", "r")
            error = f.read()
            f.close()
            if error != "Detected":
                for i in range(len(conf)):
                    if ID[i] == "stringing":
                        #lowered conf level based on testing
                        if conf[i] >= str(0.30):
                            error_file = open("/home/joe/Test/readme.txt", "w")
                            print("WARNING:ERROR DETECTED! ERROR TYPE:", ID[i])
                            error_file.write(str(ID[i]))
                            error_file.close()
                    elif ID[i] == "under extrusion":
                        #lowered conf level based on testing
                        if conf[i] >= str(0.35):
                            error_file = open("/home/joe/Test/readme.txt", "w")
                            print("WARNING:ERROR DETECTED! ERROR TYPE:", ID[i])
                            error_file.write(str(ID[i]))
                            error_file.close()
                    elif ID[i] == "warping":
                    #lowered conf level based on testing
                        if conf[i] >= str(0.60):
                            error_file = open("/home/joe/Test/readme.txt", "w")
                            print("WARNING:ERROR DETECTED! ERROR TYPE:", ID[i])
                            error_file.write(str(ID[i]))
                            error_file.close()
                    elif ID[i] == "spagehtti":
                        #lowered conf level based on testing
                        if conf[i] >= str(0.35):
                            error_file = open("/home/joe/Test/readme.txt", "w")
                            print("WARNING:ERROR DETECTED! ERROR TYPE:", ID[i])
                            error_file.write(str(ID[i]))
                            error_file.close()

        #zone.trigger(detections=detections)
        #frame = zone_annotator.annotate(scene=frame)      
        
        cv2.imshow("yolov8", frame)

        if (cv2.waitKey(30) == 27):
            break


if __name__ == "__main__":
    main()