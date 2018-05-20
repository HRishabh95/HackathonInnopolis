import yaml
import numpy as np
import cv2
import json

fn = r"data/parkinglot_1_480p.mp4"
fn_yaml = r"data/parking2.yml"
fn_out = r"data/output.avi"
config = {'save_video': True,
          'text_overlay': True,
          'parking_overlay': True,
          'parking_id_overlay': False,
          'parking_detection': True,
          'min_area_motion_contour': 60,
          'park_sec_to_wait': 3,
          'start_frame': 0} #35000

# Set capture device or file
cap = cv2.VideoCapture(fn)
# print cap.get(5) 
video_info = {'fps':    cap.get(cv2.CAP_PROP_FPS),
              'width':  int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
              'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
              'fourcc': cap.get(cv2.CAP_PROP_FOURCC),
              'num_of_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}
cap.set(cv2.CAP_PROP_POS_FRAMES, config['start_frame']) # jump to frame

# Define the codec and create VideoWriter object
if config['save_video']:
    fourcc = cv2.VideoWriter_fourcc('D','I','V','X'), ('D','I','V','X'), ('M','J','P','G'), ('X','V','I','D')
    out = cv2.VideoWriter(fn_out, -1, 25.0, #video_info['fps'], 
                          (video_info['width'], video_info['height']))



# Read YAML data (parking space polygons)
with open(fn_yaml, 'r') as stream:
    parking_data = yaml.load(stream)
parking_contours = []
parking_bounding_rects = []
parking_mask = []
for park in parking_data:
    points = np.array(park['points'])
    rect = cv2.boundingRect(points)
    points_shifted = points.copy()
    points_shifted[:,0] = points[:,0] - rect[0] # shift contour to roi
    points_shifted[:,1] = points[:,1] - rect[1]
    parking_contours.append(points)
    parking_bounding_rects.append(rect)
    mask = cv2.drawContours(np.zeros((rect[3], rect[2]), dtype=np.uint8), [points_shifted], contourIdx=-1,
                            color=255, thickness=-1, lineType=cv2.LINE_8)
    mask = mask==255
    parking_mask.append(mask)

parking_status = [False]*len(parking_data)
parking_buffer = [None]*len(parking_data)


while(cap.isOpened()):   
    spot = 0
    occupied = 0 
    # Read frame-by-frame    
    video_cur_pos = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0 # Current position of the video file in seconds
    video_cur_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) # Index of the frame to be decoded/captured next
    ret, frame = cap.read()    
    if ret == False:
        print("Capture Error")
        break
    
    # Background Subtraction
    frame_blur = cv2.GaussianBlur(frame.copy(), (5,5), 3)
    frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
    frame_out = frame.copy()
    frame_ou=frame.copy()

    if config['parking_detection']:        
        for ind, park in enumerate(parking_data):
            points = np.array(park['points'])
            rect = parking_bounding_rects[ind]
            roi_gray = frame_gray[rect[1]:(rect[1]+rect[3]), rect[0]:(rect[0]+rect[2])] # crop roi for faster calculation   

            points[:,0] = points[:,0] - rect[0] # shift contour to roi
            points[:,1] = points[:,1] - rect[1]
            status = np.std(roi_gray) < 22 and np.mean(roi_gray) > 53
            # If detected a change in parking status, save the current time
            if status != parking_status[ind] and parking_buffer[ind]==None:
                parking_buffer[ind] = video_cur_pos
            # If status is still different than the one saved and counter is open
            elif status != parking_status[ind] and parking_buffer[ind]!=None:
                if video_cur_pos - parking_buffer[ind] > config['park_sec_to_wait']:
                    parking_status[ind] = status
                    parking_buffer[ind] = None
            elif status == parking_status[ind] and parking_buffer[ind]!=None:
                parking_buffer[ind] = None                    
    spo=[]
    occ=[]
    if config['parking_overlay']:                    
        for ind, park in enumerate(parking_data):
            points = np.array(park['points'])
            if parking_status[ind]: 
                color = (0,255,0)
                spo.append(ind)
                spot = spot+1
            else: 
                color = (0,0,255)
                occ.append(ind)
                occupied = occupied+1
            cv2.drawContours(frame_out, [points], contourIdx=-1,
                             color=color, thickness=2, lineType=cv2.LINE_8)            
            moments = cv2.moments(points)        
            centroid = (int(moments['m10']/moments['m00'])-3, int(moments['m01']/moments['m00'])+3)
            cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
            cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
            cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
            cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1, cv2.LINE_AA)
            cv2.putText(frame_out, str(park['id']), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)

    data={}
    data['parking_id']=1
    data['parking_lot']=[]
    for i in range(0,29):
        if i in spo:
            data['parking_lot'].append({'id':i,'status': 1})
        else:
            data['parking_lot'].append({'id':i,'status': 0})
    with open('data.json', 'w') as outfile:
        json.dump(data,outfile)
    # write the output frame
    if config['save_video']:
        if video_cur_frame % 35 == 0: # take every 30 frames
            out.write(frame_out)    
    
    # Display video
    combine = np.concatenate((cv2.resize(frame_ou,(480,600)),cv2.resize(frame_out,(480,600))), axis=1)
    cv2.imshow('ARIVI-Raw and Predicted', combine)
    cv2.waitKey(40)
    
cap.release()
if config['save_video']: out.release()
cv2.destroyAllWindows()

