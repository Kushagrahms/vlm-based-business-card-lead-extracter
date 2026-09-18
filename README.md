<div align="center">

# 🚀 LEADLENS

### VLM-Powered Business Card Lead Extraction

**Transform business card images into structured lead information using Vision-Language AI.**

<br>

![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Qwen3-VL](https://img.shields.io/badge/Qwen3--VL-VLM-purple)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![Render](https://img.shields.io/badge/Deployment-Render-46E3B7?logo=render&logoColor=black)

</div>

---

# 📌 About

**LeadLens** is a VLM-based business card lead extraction application that automatically converts business card images into structured lead information.

Instead of manually reading and entering information from individual business cards, users can upload multiple business card images in bulk and process them using a Vision-Language Model.

The application extracts important contact and professional information, displays the results in a structured table, and allows the extracted leads to be downloaded as an Excel file.

The project uses **Qwen3-VL** for vision-language processing, **FastAPI** for the backend, **React + TypeScript** for the frontend, **SQLite** for persistence, and **Pandas** for Excel generation.

---

# 🎯 Project Objective

The application was developed to provide an end-to-end workflow for business card lead extraction.

### The application supports:

- Multiple business card image uploads
- Vision-Language Model based extraction
- Structured lead information generation
- Lead visualization
- Persistent lead storage
- Excel export
- Public web deployment

The required lead information includes:

- First Name
- Last Name
- Position / Job Title
- Company
- Location
- Phone Number
- Email Address

---

# ✨ Features

### 📤 Bulk Image Upload

Upload multiple business card images at once instead of processing cards individually.

Supported image formats include:

- PNG
- JPG
- JPEG
- WEBP

### 🤖 Vision-Language AI

Uses **Qwen3-VL** to understand the visual content of business cards and extract the required information.

### 📋 Structured Lead Extraction

Extracts business-card information into predefined structured fields.

### 👀 Lead Visualization

Extracted leads are displayed in a structured table inside the application.

### 💾 Lead Persistence

Extracted lead information is stored using SQLite.

### 📊 Excel Export

Users can export the extracted lead information into an Excel spreadsheet for further use.

### ☁️ Public Deployment

The web application is publicly deployed and accessible through a web URL.

---

# 🖥️ Application Preview

## 🏠 Landing Page

The LeadLens landing page provides the main interface for starting the business card extraction workflow.

<img width="1891" height="907" alt="Screenshot 2026-09-18 182639" src="https://github.com/user-attachments/assets/c61ff904-40c5-4169-9348-209cff74fd56" />

---

## 📤 Business Card Upload

Users can select one or multiple business card images and start the extraction process.

<img width="1656" height="697" alt="Screenshot 2026-09-18 182657" src="https://github.com/user-attachments/assets/0b9827eb-94ce-4850-a6d7-b1b414cb42ce" />


---

## 📋 Extracted Leads

After processing, the extracted lead information is displayed in a structured table.

<img width="1585" height="732" alt="Screenshot 2026-09-18 182708" src="https://github.com/user-attachments/assets/91040431-ef9e-4203-9cca-d8ec7d426c05" />


---

## 📊 Excel Export

The extracted lead information can be exported into an Excel file.

<img width="1742" height="413" alt="Screenshot 2026-09-18 211518" src="https://github.com/user-attachments/assets/cf25194d-d830-430d-81f5-0ff64786372c" />


---

# 🏗️ System Architecture

The application is divided into several components responsible for user interaction, API processing, VLM inference, data persistence, and output generation.

<img width="1312" height="1199" alt="7a229d58-ad3e-4598-965d-38d938d532ea" src="https://github.com/user-attachments/assets/f1b4b95d-e698-4cc8-9c13-a7563f1981c8" />


### Architecture Components

| Component | Responsibility |
|---|---|
| **User** | Uploads business card images and receives extracted results |
| **React + TypeScript Frontend** | Handles image upload, result visualization, and Excel download |
| **FastAPI Backend** | Receives images, communicates with the VLM, validates results, stores data, and provides API endpoints |
| **Kaggle VLM Environment** | Provides GPU-enabled runtime for Qwen3-VL inference |
| **Qwen3-VL** | Processes business card images and extracts structured information |
| **SQLite Database** | Stores extracted lead information |
| **Pydantic** | Validates and structures extracted data |
| **Pandas** | Processes lead data and generates Excel output |
| **Excel Output** | Provides the final downloadable lead list |

### Data Flow

```text
User
  │
  │ Business Card Images
  ▼
React + TypeScript Frontend
  │
  │ HTTP Request
  ▼
FastAPI Backend
  │
  │ Image + Prompt
  ▼
Kaggle GPU Environment
  │
  │ Qwen3-VL
  ▼
Structured Lead Data
  │
  ▼
FastAPI Backend
  │
  ├──────────────► SQLite Database
  │
  ▼
Pydantic Validation
  │
  ▼
Lead Results
  │
  ▼
Pandas
  │
  ▼
Excel File
