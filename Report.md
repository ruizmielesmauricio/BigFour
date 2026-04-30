# 📊 Big Four Thrash Metal Analysis — Technical Report

---

## 1. Introduction

This project aims to analyze and compare the musical and audience characteristics of the “Big Four” of thrash metal: **Metallica, Megadeth, Slayer, and Anthrax**.  

The objective is to combine multiple data sources to build a unified dataset that enables analysis of popularity, discography trends, and musical features such as tempo (BPM).  

The final output includes both analytical insights and an interactive dashboard built using **Streamlit**.

---

## 2. Data Sources

The dataset was constructed by integrating multiple external APIs and datasets:

### MusicBrainz API
- Extracted clean studio albums and track listings  
- Provided structured discography data (albums, release dates, track names)

### Last.fm API
- Retrieved track-level popularity metrics:
  - Playcount (streams)
  - Listener counts

### GetSongBPM API
- Enriched tracks with musical features:
  - BPM (tempo)
  - Key

### Supplementary Dataset (Audio Features)
- Attempted integration for tempo/mood  
- Low coverage → replaced by GetSongBPM

---

## 3. Data Pipeline

The pipeline followed a modular **ETL (Extract, Transform, Load)** approach.

### 3.1 Extraction
- Retrieved artist IDs from MusicBrainz  
- Extracted:
  - Studio albums only (filtered by release type)
  - Tracks per album  
- Queried:
  - Last.fm → popularity metrics  
  - GetSongBPM → tempo data  

---

### 3.2 Transformation

#### Data Cleaning
- Removed duplicates across:
  - Track name + album + artist  
- Filtered non-studio releases  
- Removed invalid entries (e.g., *“Crazy Sheep”*)  
- Standardized numeric fields (playcount, listeners, BPM)

#### Data Integration
- Merged datasets on:
  - `artist + track_name`  
- Resolved mismatches between APIs  

**Coverage achieved:**
- ~87% BPM coverage  
- Full coverage for popularity metrics  

#### Feature Engineering

**Album-level features**
- Total tracks  
- Total playcount  
- Total listeners  
- Average BPM  
- BPM coverage %

**Track-level features**
- Rank within artist  
- Popularity metrics  

**Comparative metrics**
- Popularity ratio matrix  
- Dominance score (% difference vs others)

---

## 4. Exploratory Data Analysis (EDA)

### 4.1 Track-Level Analysis
- Identified top tracks per artist based on playcount  
- Removed duplicate tracks across albums  

**Observations:**
- High concentration of streams in a small subset of tracks  
- Re-release duplication present in raw data  

---

### 4.2 Album-Level Analysis
- Aggregated track data to album level  

**Findings:**
- Certain albums dominate discographies  
- Significant variation in BPM across albums  

---

### 4.3 BPM Analysis
- Calculated average BPM per album  
- Identified:
  - Fastest albums  
  - Slowest albums  

**Limitation:**
- Missing BPM values → partial coverage  
- Addressed using BPM coverage metrics  

---

### 4.4 Popularity Analysis
- Compared total streams and listeners across bands  

Constructed:
- **Dominance score** → average % advantage vs others  
- **Ratio matrix** → relative popularity  

**Key insight:**
> Metallica consistently dominates in total streams and audience reach  

---

## 5. Comparative Analysis

### 5.1 Album vs Album Comparison
- Interactive comparison between selected albums  

Metrics:
- Average BPM  
- Total listeners  
- Total playcount  

---

### 5.2 Band Overview Analysis

For each band:
- Total listeners  
- Most vs least popular album  
- Fastest vs slowest album  
- Discography ranking by:
  - BPM  
  - Total streams  

---

### 5.3 Popularity Matrix

#### Ratio Matrix
Interprets popularity as:
