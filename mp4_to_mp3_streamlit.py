import streamlit as st
import tempfile
import os
import datetime
import json
import subprocess
import shutil

# Controleer of ffmpeg beschikbaar is
def has_ffmpeg():
    try:
        # Controleer of ffmpeg geïnstalleerd is
        ffmpeg_version = subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

# Functie om MP4 naar MP3 te converteren met ffmpeg
def convert_mp4_to_mp3(input_file, output_file, bitrate="192k"):
    try:
        cmd = [
            'ffmpeg',
            '-i', input_file,            # input file
            '-vn',                       # verwijder video
            '-acodec', 'libmp3lame',     # audio codec
            '-ab', bitrate,              # audio bitrate
            '-ar', '44100',              # audio sample rate
            '-y',                        # overschrijf bestaand bestand
            output_file                  # output file
        ]
        
        # Voer de ffmpeg-opdracht uit
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            error_message = stderr.decode('utf-8') if stderr else "Onbekende fout bij conversie"
            raise Exception(f"FFMPEG fout (code {process.returncode}): {error_message}")
        
        return True
    except Exception as e:
        raise Exception(f"Conversie fout: {str(e)}")

# Eerste run: installeer ffmpeg als het niet gevonden wordt
if not has_ffmpeg():
    st.warning("FFMPEG wordt geïnstalleerd...")
    # Deze poging wordt alleen in de cloud gedaan en niet lokaal
    try:
        subprocess.check_call(["apt-get", "update"])
        subprocess.check_call(["apt-get", "install", "-y", "ffmpeg"])
        st.success("FFMPEG succesvol geïnstalleerd!")
    except Exception as e:
        st.error(f"Kon FFMPEG niet installeren: {str(e)}")
        st.info("Gebruik de app lokaal of neem contact op met de ontwikkelaar")
        st.stop()

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
    if st.button("Converteren naar MP3", type="primary"):
        # Toon laadstatus met spinner
        with st.spinner(f"Bezig met converteren naar {kwaliteit}kbps MP3... Dit kan even duren."):
            try:
                # MP4 naar MP3 converteren met FFMPEG
                convert_mp4_to_mp3(tmp_mp4_path, output_path, bitrate=f"{kwaliteit}k")
                
                # Sla conversie op in geschiedenis
                opslaan_geschiedenis(output_filename, kwaliteit)
                
                st.success("Conversie voltooid! 🎉 Download je MP3-bestand.")
                
                # Als een downloadpad is opgegeven, sla het bestand daar op
                if download_pad and os.path.isdir(download_pad):
                    final_path = os.path.join(download_pad, output_filename)
                    import shutil
                    shutil.copy(output_path, final_path)
                    st.success(f"Bestand opgeslagen in: {final_path}")
                
                # Download knop weergeven (altijd beschikbaar)
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"Download {output_filename}",
                        data=f,
                        file_name=output_filename,
                        mime="audio/mpeg",
                        key="download_button"
                    )
            except Exception as e:
                st.error(f"Fout bij conversie: {str(e)}")
            finally:
                # Opruimen
                if os.path.exists(tmp_mp4_path):
                    os.remove(tmp_mp4_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
else:
    st.info("Upload een MP4-bestand om te beginnen")

# Footer
st.markdown("---")
st.caption("MP4 naar MP3 Converter | Ontwikkeld met ❤️ en Streamlit")