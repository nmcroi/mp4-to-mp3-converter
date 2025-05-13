# MP4 naar MP3 Converter (Streamlit Webapp)

Een eenvoudige webapplicatie waarmee je een MP4-bestand kunt uploaden en de audio extraheert naar een MP3-bestand. Geschikt om online te draaien via [Streamlit Community Cloud](https://share.streamlit.io/).

## Functionaliteiten
- Upload een MP4-bestand (video)
- Kies de audiokwaliteit (64-320 kbps)
- Geef een aangepaste bestandsnaam op (optioneel)
- Bekijk de conversiegeschiedenis
- Download het geëxtraheerde MP3-bestand

## Lokaal draaien

1. Installeer de benodigde packages:

```bash
pip install -r requirements.txt
```

2. Start de applicatie:

```bash
streamlit run mp4_to_mp3_streamlit.py
```

## Online via Streamlit Cloud (GitHub)
1. Zet `mp3_to_mp4_streamlit.py` en `requirements.txt` in een nieuwe GitHub-repository.
2. Ga naar [https://share.streamlit.io/](https://share.streamlit.io/) en koppel je repository.
3. Selecteer `mp3_to_mp4_streamlit.py` als hoofd-bestand.
4. De app wordt automatisch online gezet en is publiek toegankelijk.

# Excel Bewerker App

Een eenvoudige webapplicatie waarmee je Excel bestanden kunt uploaden, bewerken en downloaden.

## Functionaliteiten

- Upload Excel bestanden (.xlsx, .xls)
- Bekijk een preview van de data
- Selecteer welke kolommen je wilt behouden
- Filter rijen op basis van kolomwaarden
- Sorteer de data op een kolom
- Download het bewerkte bestand als Excel

## Installatie

1. Installeer de benodigde packages:

```bash
pip install -r requirements.txt
```

2. Start de applicatie:

```bash
streamlit run app.py
```

## Gebruik

1. Open de webbrowser en ga naar de URL die wordt getoond in de terminal (meestal http://localhost:8501)
2. Upload een Excel bestand met de uploader
3. Bewerk het bestand met de beschikbare opties
4. Download het bewerkte bestand

## Delen met collega's

Om deze applicatie te delen met collega's, heb je twee opties:

1. **Lokaal netwerk**: Run de app met `streamlit run app.py --server.address=0.0.0.0` om hem beschikbaar te maken op je lokale netwerk. Collega's kunnen dan verbinding maken via jouw IP-adres.

2. **Streamlit Cloud**: Deploy de app naar [Streamlit Cloud](https://streamlit.io/cloud) voor een publiek toegankelijke URL.

3. **Alternatieve hosting**: Deploy de app naar services zoals Heroku, AWS, or Google Cloud Platform.
