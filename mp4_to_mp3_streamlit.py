import streamlit as st
import tempfile
import os
import datetime
import json
import io

# Functie om MP4 naar MP3 te converteren met pure Python
def convert_mp4_to_mp3(input_file, output_file, bitrate=192000):
    try:
        # We gebruiken Python's ingebouwde bibliotheken om met audiobestanden te werken
        import wave
        from pydub import AudioSegment
        
        # Laad MP4-bestand
        st.info("MP4-bestand laden...")
        audio = AudioSegment.from_file(input_file, format="mp4")
        
        # Stel de audiokwaliteit (bitrate) in
        st.info("Audio-instellingen toepassen...")
        
        # Exporteren als MP3
        st.info("Exporteren naar MP3...")
        audio.export(output_file, format="mp3", bitrate=f"{int(bitrate/1000)}k")
        
        return True
    except ImportError:
        st.error("Pydub is niet geïnstalleerd. We installeren het nu...")
        import sys
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])
            st.success("Pydub succesvol geïnstalleerd! Probeer opnieuw.")
            # Probeer opnieuw na installatie
            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_file, format="mp4")
            audio.export(output_file, format="mp3", bitrate=f"{int(bitrate/1000)}k")
            return True
        except Exception as e:
            st.error(f"Kon pydub niet installeren: {str(e)}")
            return False
    except Exception as e:
        st.error(f"Fout bij conversie: {str(e)}")
        return False

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