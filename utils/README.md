# Convert CSV to Json for import DRES
## Task type
- TKIS: 
{
   "id": "09039b2c-92e4-4f31-b10d-08f9b00ea6d6", - generated
   "name": "tkis-query-01", - get from csv
   "taskGroup": "tkis",
   "taskType": "Textual Known Item Search",
   "duration": 300,
   "collectionId": "796ac77f-44de-44b8-8191-656395621088", - fixed
   "targets": [
    {
     "type": "MEDIA_ITEM_TEMPORAL_RANGE",
     "target": "1de7a6f7-46e6-47cc-9154-37c3eda6c1ab", # ignore
     "range": {
      "start": {
       "value": "611000",
       "unit": "MILLISECONDS"
      },
      "end": {
       "value": "635000",
       "unit": "MILLISECONDS"
      }
     },
     "item": {
      "mediaItemId": "1de7a6f7-46e6-47cc-9154-37c3eda6c1ab", #ignore
      "name": "K05_V018",
      "type": "VIDEO",
      "collectionId": "796ac77f-44de-44b8-8191-656395621088",
      "location": "K05_V018.mp4",
      "durationMs": 846566,
      "fps": 30
     }
    }
   ],
   "hints": [ # fixed time, change description based on CSV separated by ";"
    {
     "type": "TEXT",
     "start": 0,
     "end": 60, 
     "description": "Một con robot có 4 chân gắn với 4 bánh xe chạy trên đồng cỏ. ", 
     "dataType": "text/plain"
    },
    {
     "type": "TEXT",
     "start": 60,
     "end": 120,
     "description": "Cảnh sau có những con bò đứng kế bên con robot. ",
     "dataType": "text/plain"
    },
    {
     "type": "TEXT",
     "start": 120,
     "description": "Đoạn clip kết thúc bằng cảnh phỏng vấn người trong nhóm làm ra con robot để mô tả các phương thức hoạt động và sự hữu ích của nó.",
     "dataType": "text/plain"
    }
   ],
   "comment": ""
  },


QA-KIS

{
   "id": "367b9f77-39ff-42ae-9238-2225eff20b73",
   "name": "qa-query-01",
   "taskGroup": "qa-kis",
   "taskType": "qa-kis",
   "duration": 300,
   "collectionId": "796ac77f-44de-44b8-8191-656395621088",
   "targets": [
    {
     "type": "TEXT",
     "target": "QA-6-L25_V058-729000-930000"
    }
   ],
   "hints": [ # Always keep the question first (detect by split part before "?") in every description. Separates description based on csv as TKIS (separated by ";")
    {
     "type": "TEXT",
     "start": 0,
     "description": "Hỏi chữ số này là số mấy? Đây là câu 3 trong bài tập vận dụng. Các dữ kiện của đề bài bao gồm khoảng cách giữa AB là một số có 2 chữ số có chữ số hàng chục bằng chữ số hàng đơn vị. Chữ số này còn dùng để làm một điều kiện khác trong bài và được nêu ra ngay trong cùng câu mở đầu. Đáp án của bài là C. ",
     "dataType": "text/plain"
    }
   ],
   "comment": ""
},

TRAKE

  {
   "id": "6b459ebe-02a0-4eec-962b-e815af8f5cac",
   "name": "trake-query-01",
   "taskGroup": "trake",
   "taskType": "trake",
   "duration": 300,
   "collectionId": "796ac77f-44de-44b8-8191-656395621088",
   "targets": [
    {
     "type": "TEXT",
     "target": "TR-L26_V176-4725,4875"
    }
   ],
   "hints": [ # Don't need to separates;
    {
     "type": "TEXT",
     "start": 0,
     "description": "Đây là một cảnh nấu món cá.\nE1: Người đầu bếp khuấy một hỗn hợp nước sốt. Lấy khoảnh khắc người đầu bếp lấy muỗng chạm vào nước sốt lần đầu tiên.\nE2: Người đầu bếp rưới nước sốt vào nồi. Trong nồi có một khoanh cá và phía trên là 1 quả ớt. Miếng cá này được đặt lên trên các miếng thịt. Lấy khoảnh khắc nước sốt được cho hoàn toàn hết vào nồi.",
     "dataType": "text/plain"
    }
   ],
   "comment": ""
  },