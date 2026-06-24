# 🇮🇩 Indonesian Document OCR

An OCR API for extracting structured information from Indonesian documents using **FastAPI**, **PaddleOCR**, and **OpenCV**.

The project supports automatic text recognition and field parsing, returning clean JSON responses that are easy to integrate into web or mobile applications.

---

## ✨ Features

- OCR-based text recognition
- Image preprocessing with OpenCV
- Structured data extraction
- REST API with FastAPI
- JSON response output
- Modular parser architecture
- Easy to extend for additional document types

---

## 📄 Supported Documents

| Document | Status |
|-----------|---------|
| KTP (Identity Card) | ✅ |
| Kartu Keluarga (KK) | ✅ |
| Birth Certificate (Akta Kelahiran) | ✅ |
| Student ID Card (Kartu Pelajar) | ✅ |

---

## 🛠 Tech Stack

- Python 3.12
- FastAPI
- PaddleOCR
- OpenCV
- Pydantic
- Uvicorn

---

## 📁 Project Structure

```text
ocr-project/
│
├── app/
│   ├── parsers/
│   ├── schemas/
│   ├── services/
│   ├── preprocess/
│   ├── extractors/
│   ├── routes/
│   ├── utils/
│   └── main.py
│
├── uploads/
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

Clone repository:

```bash
git clone https://github.com/your-username/indonesian-document-ocr.git

cd indonesian-document-ocr
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
uvicorn app.main:app --reload
```

Server will run at:

```text
http://127.0.0.1:8000
```

---

## 📌 API Endpoints

### OCR KTP

```http
POST /ocr/ktp
```

### OCR Kartu Keluarga

```http
POST /ocr/kk
```

### OCR Birth Certificate

```http
POST /ocr/akta
```

### OCR Student ID Card

```http
POST /ocr/kartu-pelajar
```

---

## 📥 Example Request

Upload image:

```bash
curl -X POST \
-F "file=@ktp.jpg" \
http://localhost:8000/ocr/ktp
```

---

## 📤 Example Response

```json
{
  "status": "success",
  "code": 200,
  "message": "KTP data extracted successfully",
  "data": {
    "nik": "3171234567890123",
    "nama": "MIRASETIAWAN",
    "tempat_lahir": "JAKARTA",
    "tanggal_lahir": "18-02-1986",
    "jenis_kelamin": "PEREMPUAN",
    "alamat": "JL MERDEKA NO 10"
  }
}
```

---

## 📚 Future Improvements

- Passport OCR
- Driving License (SIM) OCR
- NPWP OCR
- PDF support
- Table extraction improvements
- Multi-language support
- Docker deployment

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork this repository and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you find this project useful, please consider giving it a ⭐ on GitHub.