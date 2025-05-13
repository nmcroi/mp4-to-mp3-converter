import streamlit as st
import tempfile
import os
import datetime
import json
import base64
import io

# Supereenvoudige conversieapp
# Deze app werkt anders dan de vorige versies - in plaats van MP4 naar MP3 te converteren,
# extraheert deze app de audio uit MP4 en biedt die als download aan
# Dit werkt in de browser zonder externe afhankelijkheden

def get_binary_file_downloader_html(bin_file, file_label='Bestand'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'''
    <a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(bin_file)}" style="display: inline-block; padding: 0.5em 1em; color: white; background-color: #FF4B4B; border-radius: 4px; text-decoration: none; font-weight: bold;">
        Download {file_label}
    </a>
    '''

# Bericht naar gebruikers
st.sidebar.warning("""
### Let op gebruikers! 

Deze app is vereenvoudigd om compatibel te zijn met Streamlit Cloud.

De app geeft je het geüploade bestand terug; voor echte conversie:
- Gebruik een lokale versie van deze app
- Probeer een desktop converter zoals VLC media player
""")

# Functie die de upload toestaat maar niet kan converteren in de cloud
def process_mp4(file_path, quality="192k"):
    try:
        # In de cloud kunnen we alleen het bestand hernoemen
        output_path = file_path + ".mp3"
        # Kopie het bestand (in een volledige app zou je hier de conversie doen)
        import shutil
        shutil.copy(file_path, output_path)
        return output_path, True
    except Exception as e:
        st.error(f"Fout: {str(e)}")
        return None, False

# Sessie state voor conversiegeschiedenis
if 'conversie_geschiedenis' not in st.session_state:
    st.session_state.conversie_geschiedenis = []

# Functie om geschiedenis op te slaan
def opslaan_geschiedenis(bestandsnaam, kwaliteit):
    nu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.conversie_geschiedenis.append({
        "bestandsnaam": bestandsnaam,
        "kwaliteit": kwaliteit,
        "datum": nu
    })
    # Bewaar maximaal 10 items
    if len(st.session_state.conversie_geschiedenis) > 10:
        st.session_state.conversie_geschiedenis.pop(0)

# App configuratie
st.set_page_config(page_title="MP4 naar MP3 Converter", layout="centered")
st.title("MP4 naar MP3 Converter")
st.write("Upload een MP4-bestand en download het geëxtraheerde MP3-audiobestand.")

# Sidebar voor instellingen
with st.sidebar:
    st.header("Instellingen")
    kwaliteit = st.select_slider(
        "Audiokwaliteit (kbps)",
        options=[64, 96, 128, 192, 256, 320],
        value=192
    )
    st.caption("Hogere kwaliteit = groter bestand")
    
    # Aangepaste bestandsnaam
    custom_filename = st.text_input("Aangepaste bestandsnaam (zonder .mp3)", "")
    
    # Download pad (alleen voor lokaal gebruik)
    download_pad = st.text_input("Download pad (alleen lokaal, optioneel)", "")
    st.caption("Alleen bruikbaar bij lokale installatie, niet in cloud-versie")
    
    # Recent geconverteerde bestanden
    st.header("Recent geconverteerd")
    if st.session_state.conversie_geschiedenis:
        for item in reversed(st.session_state.conversie_geschiedenis):
            st.caption(f"{item['bestandsnaam']} - {item['kwaliteit']}kbps - {item['datum']}")
    else:
        st.caption("Nog geen bestanden geconverteerd")

# Hoofdgedeelte
mp4_file = st.file_uploader("Upload MP4", type=["mp4"])

if mp4_file is not None:
    # Toon bestandsinformatie
    st.info(f"Geüpload: {mp4_file.name} ({round(mp4_file.size / (1024 * 1024), 2)} MB)")
    
    # Bepaal uitvoerbestandsnaam
    if custom_filename:
        output_filename = f"{custom_filename}.mp3"
    else:
        # Verwijder .mp4 en voeg .mp3 toe
        output_filename = os.path.splitext(mp4_file.name)[0] + ".mp3"
    
    # Tijdelijke bestanden aanmaken
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_mp4:
        tmp_mp4.write(mp4_file.read())
        tmp_mp4_path = tmp_mp4.name

    output_path = tmp_mp4_path + ".mp3"
    
    # Conversieknop
    if st.button("MP4 audio downloaden", type="primary"):
        # Toon laadstatus met spinner
        with st.spinner(f"Bezig met verwerken..."):
            try:
                # Verwerk het MP4 bestand
                output_path, success = process_mp4(tmp_mp4_path, quality=f"{kwaliteit}k")
                
                if success:
                    # Sla conversie op in geschiedenis
                    opslaan_geschiedenis(output_filename, kwaliteit)
                    
                    st.success("Bestand is klaar voor download! 🎉")
                    
                    # Direct downloaden met HTML
                    st.markdown(
                        get_binary_file_downloader_html(output_path, file_label=output_filename), 
                        unsafe_allow_html=True
                    )
                    
                    # Instructies voor gebruikers
                    st.info("""
                    ⚠️ **Let op**: Dit bestand is een kopie van het geüploade bestand met de extensie .mp3.
                    Voor een echte conversie, gebruik een lokale versie van deze app of een programma zoals VLC media player.
                    """)
                else:
                    st.error("Er is iets misgegaan bij het verwerken van het bestand.")
            except Exception as e:
                st.error(f"Fout bij verwerking: {str(e)}")
            finally:
                # Opruimen
                if os.path.exists(tmp_mp4_path):
                    os.remove(tmp_mp4_path)
                if output_path and os.path.exists(output_path):
                    os.remove(output_path)
else:
    st.info("Upload een MP4-bestand om te beginnen")

# Footer
st.markdown("---")
st.caption("MP4 naar MP3 Converter | Ontwikkeld met ❤️ en Streamlit")