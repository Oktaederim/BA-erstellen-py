import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

# Seitenkonfiguration
st.set_page_config(
    page_title="Betriebsanweisungs-Generator",
    page_icon="⚠️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1 {
        color: white !important;
        text-align: center;
        padding: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .subtitle {
        color: white;
        text-align: center;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Vorlagen für verschiedene Betriebsanweisungskategorien
VORLAGEN = {
    "maschine": {
        "name": "⚙️ Maschinen und Anlagen",
        "farbe": colors.HexColor("#FF6B35"),
        "beispiele": {
            "anwendungsbereich": "Bedienung der CNC-Fräsmaschine im Produktionsbereich",
            "gefahren": "• Quetschgefahr durch bewegliche Maschinenteile\n• Verletzungsgefahr durch Späne\n• Lärmbelastung\n• Gefahr durch rotierende Werkzeuge",
            "schutzmassnahmen": "• Schutzeinrichtungen dürfen nicht entfernt werden\n• Gehörschutz und Schutzbrille tragen\n• Lange Haare zusammenbinden\n• Keine weite Kleidung tragen\n• Nur eingewiesene Personen dürfen die Maschine bedienen",
            "stoerungen": "• Maschine sofort ausschalten (NOT-AUS)\n• Vorgesetzten informieren\n• Nicht selbst reparieren\n• Maschine gegen Wiedereinschalten sichern\n• Störung dokumentieren",
            "unfaelle": "• Verletzte Person aus dem Gefahrenbereich bringen\n• Erste Hilfe leisten\n• Notruf 112\n• Durchgangsarzt kontaktieren\n• Vorgesetzten informieren\n• Unfallstelle nicht verändern",
            "instandhaltung": "• Nur durch befugte Personen\n• Maschine vor Wartung ausschalten und gegen Wiedereinschalten sichern\n• Wartungsplan beachten\n• Wartungsarbeiten dokumentieren",
            "entsorgung": "• Späne in vorgesehenen Behältern sammeln\n• Kühlschmierstoffe ordnungsgemäß entsorgen\n• Altöl in gekennzeichnete Behälter füllen"
        }
    },
    "gefahrstoff": {
        "name": "☠️ Gefahrstoffe",
        "farbe": colors.HexColor("#E63946"),
        "beispiele": {
            "anwendungsbereich": "Umgang mit Lösungsmitteln in der Lackiererei",
            "gefahren": "• Gesundheitsschädlich bei Einatmen\n• Reizend für Augen und Haut\n• Leichtentzündlich\n• Umweltgefährdend\n• Kann Schläfrigkeit und Benommenheit verursachen",
            "schutzmassnahmen": "• Nur in gut belüfteten Räumen verwenden\n• Atemschutz, Schutzhandschuhe und Schutzbrille tragen\n• Von Zündquellen fernhalten\n• Nicht rauchen\n• Hautkontakt vermeiden\n• Nach Arbeit Hände waschen",
            "stoerungen": "• Bei Verschütten: Räumlichkeit lüften\n• Mit Bindemittel aufnehmen\n• Zündquellen entfernen\n• Vorgesetzten informieren\n• Kontaminierte Kleidung wechseln",
            "unfaelle": "• Bei Hautkontakt: Sofort mit viel Wasser abwaschen\n• Bei Augenkontakt: 15 Minuten mit Wasser spülen, Arzt aufsuchen\n• Bei Einatmen: An die frische Luft, Arzt konsultieren\n• Notruf 112 bei schweren Vergiftungen\n• Giftnotruf kontaktieren",
            "instandhaltung": "• Behälter dicht verschlossen halten\n• Regelmäßige Kontrolle der Lagerbedingungen\n• Absauganlage warten\n• Nur Originalbehälter verwenden\n• Kühl und trocken lagern",
            "entsorgung": "• Nicht in Ausguss oder Mülltonne\n• In gekennzeichneten Behältern sammeln\n• Durch Fachfirma entsorgen lassen\n• Sicherheitsdatenblatt beachten"
        }
    },
    "taetigkeit": {
        "name": "👷 Tätigkeiten",
        "farbe": colors.HexColor("#457B9D"),
        "beispiele": {
            "anwendungsbereich": "Arbeiten auf Leitern und Gerüsten",
            "gefahren": "• Absturzgefahr aus der Höhe\n• Umkippen der Leiter\n• Herabfallende Gegenstände\n• Abrutschen auf Sprossen\n• Elektrische Gefährdung bei Arbeiten an Stromleitungen",
            "schutzmassnahmen": "• Nur geprüfte Leitern verwenden\n• Leiter auf festem, ebenen Untergrund aufstellen\n• Anlegewinkel von 65-75° einhalten\n• Nicht auf obersten zwei Sprossen stehen\n• Absturzsicherung ab 2m Höhe\n• Arbeitsbereich absperren\n• Festes Schuhwerk tragen",
            "stoerungen": "• Bei beschädigter Leiter: Nicht verwenden, kennzeichnen\n• Vorgesetzten informieren\n• Leiter außer Betrieb nehmen\n• Bei instabilem Untergrund: Arbeit einstellen",
            "unfaelle": "• Notruf 112\n• Erste Hilfe leisten\n• Verletzte Person nicht bewegen bei Verdacht auf Wirbelsäulenverletzung\n• Unfallstelle sichern\n• Zeugen benennen\n• Durchgangsarzt aufsuchen",
            "instandhaltung": "• Regelmäßige Sichtprüfung vor Benutzung\n• Jährliche Prüfung durch befähigte Person\n• Leitern trocken lagern\n• Beschädigungen sofort melden\n• Prüfplakette kontrollieren",
            "entsorgung": "• Defekte Leitern fachgerecht entsorgen\n• Nicht reparieren lassen\n• Holzleitern: Restmüll oder Sperrmüll\n• Aluminiumleitern: Wertstoffhof"
        }
    },
    "biologisch": {
        "name": "🦠 Biologische Arbeitsstoffe",
        "farbe": colors.HexColor("#2A9D8F"),
        "beispiele": {
            "anwendungsbereich": "Umgang mit biologischen Arbeitsstoffen im Labor",
            "gefahren": "• Infektionsgefahr durch Krankheitserreger\n• Allergische Reaktionen\n• Kontamination\n• Nadelstichverletzungen\n• Aerosolbildung",
            "schutzmassnahmen": "• Laborkittel, Handschuhe und ggf. Atemschutz tragen\n• Hygienemaßnahmen strikt einhalten\n• Hände desinfizieren\n• Nicht essen, trinken oder rauchen\n• Arbeiten in Sicherheitswerkbank\n• Schutzimpfungen wahrnehmen",
            "stoerungen": "• Bei Kontamination: Bereich absperren\n• Desinfektion durchführen\n• Biologischen Sicherheitsbeauftragten informieren\n• Vorfall dokumentieren\n• Ggf. Arbeitsmediziner konsultieren",
            "unfaelle": "• Bei Verletzung: Wunde bluten lassen, desinfizieren\n• Betriebsarzt aufsuchen\n• Durchgangsarzt bei schweren Verletzungen\n• Vorfall dokumentieren\n• Bei Kontamination: Sofort desinfizieren\n• Postexpositionsprophylaxe prüfen",
            "instandhaltung": "• Regelmäßige Wartung der Sicherheitswerkbank\n• Autoklavierung von Geräten\n• Dekontamination der Arbeitsflächen\n• Funktionsprüfung der Sicherheitseinrichtungen\n• Filterwechsel nach Plan",
            "entsorgung": "• Autoklavierung von kontaminierten Materialien\n• Entsorgung in speziellen Biohazard-Behältern\n• Durch Fachfirma entsorgen lassen\n• Kanülen in durchstichsicheren Behältern\n• Entsorgungsnachweis führen"
        }
    }
}

def create_pdf(data):
    """Erstellt PDF-Betriebsanweisung"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.white,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        fontName='Helvetica'
    )
    
    story = []
    
    # Header
    kategorie = data['kategorie']
    farbe = VORLAGEN[kategorie]['farbe']
    
    story.append(Paragraph("BETRIEBSANWEISUNG", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Info-Tabelle
    info_data = [
        ["Arbeitsbereich:", data['arbeitsbereich']],
        ["Tätigkeit/Maschine:", data['titel']],
        ["Erstellt am:", datetime.now().strftime("%d.%m.%Y")],
        ["Erstellt von:", data['ersteller']]
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 11*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#333333")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 1*cm))
    
    # Abschnitte
    abschnitte = [
        ("1. ANWENDUNGSBEREICH", data['anwendungsbereich']),
        ("2. GEFAHREN FÜR MENSCH UND UMWELT", data['gefahren']),
        ("3. SCHUTZMAẞNAHMEN UND VERHALTENSREGELN", data['schutzmassnahmen']),
        ("4. VERHALTEN BEI STÖRUNGEN", data['stoerungen']),
        ("5. VERHALTEN BEI UNFÄLLEN / ERSTE HILFE", data['unfaelle']),
        ("6. INSTANDHALTUNG / ENTSORGUNG", data['instandhaltung'] + "\n\n" + data['entsorgung'])
    ]
    
    for titel, inhalt in abschnitte:
        heading_data = [[Paragraph(titel, heading_style)]]
        heading_table = Table(heading_data, colWidths=[16*cm])
        heading_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), farbe),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(heading_table)
        story.append(Spacer(1, 0.3*cm))
        
        if inhalt:
            text_lines = inhalt.replace('\n', '<br/>')
            story.append(Paragraph(text_lines, normal_style))
        
        story.append(Spacer(1, 0.5*cm))
    
    # Unterschriften
    story.append(Spacer(1, 1*cm))
    
    unterschrift_data = [
        ["_" * 40, "_" * 40],
        ["Datum, Unterschrift Ersteller", "Datum, Unterschrift Vorgesetzter"]
    ]
    
    unterschrift_table = Table(unterschrift_data, colWidths=[8*cm, 8*cm])
    unterschrift_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(unterschrift_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Hauptanwendung
def main():
    st.markdown("<h1>⚠️ Betriebsanweisungs-Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Erstellen Sie professionelle Betriebsanweisungen für Ihre Arbeitssicherheit</p>", unsafe_allow_html=True)
    
    # Warnung
    st.markdown("""
        <div class='warning-box'>
            <strong>⚠️ Wichtiger Hinweis:</strong> Betriebsanweisungen sind wichtige Dokumente für die Arbeitssicherheit. 
            Bitte prüfen Sie alle Angaben sorgfältig und lassen Sie diese von einer Fachkraft für Arbeitssicherheit freigeben.
        </div>
    """, unsafe_allow_html=True)
    
    # Layout mit zwei Spalten
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 1️⃣ Kategorie wählen")
        
        kategorie_option = st.radio(
            "Wählen Sie eine Kategorie:",
            options=list(VORLAGEN.keys()),
            format_func=lambda x: VORLAGEN[x]['name'],
            key="kategorie"
        )
        
        st.markdown("---")
        
        if st.button("📋 Beispiel laden", use_container_width=True):
            st.session_state.beispiel_laden = True
        
        if st.button("🔄 Formular zurücksetzen", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith('input_'):
                    del st.session_state[key]
            st.session_state.beispiel_laden = False
            st.rerun()
    
    with col2:
        st.markdown("### 2️⃣ Angaben eingeben")
        
        # Initialisiere Beispiel-Werte
        beispiele = VORLAGEN[kategorie_option]['beispiele'] if st.session_state.get('beispiel_laden', False) else {}
        
        with st.form("betriebsanweisung_form"):
            arbeitsbereich = st.text_input(
                "Arbeitsbereich / Abteilung *",
                value=beispiele.get('anwendungsbereich', '').split(' im ')[1] if ' im ' in beispiele.get('anwendungsbereich', '') else '',
                placeholder="z.B. Produktionshalle 2, Werkstatt, Labor",
                key="input_arbeitsbereich"
            )
            
            titel = st.text_input(
                "Tätigkeit / Maschine / Gefahrstoff *",
                value=beispiele.get('anwendungsbereich', '').split(' im ')[0] if ' im ' in beispiele.get('anwendungsbereich', '') else beispiele.get('anwendungsbereich', ''),
                placeholder="z.B. CNC-Fräsmaschine, Lösungsmittel, Leiterarbeiten",
                key="input_titel"
            )
            
            ersteller = st.text_input(
                "Erstellt von *",
                placeholder="Ihr Name",
                key="input_ersteller"
            )
            
            st.markdown("---")
            
            anwendungsbereich = st.text_area(
                "Anwendungsbereich *",
                value=beispiele.get('anwendungsbereich', ''),
                height=100,
                placeholder="Beschreiben Sie den Anwendungsbereich...",
                key="input_anwendungsbereich"
            )
            
            gefahren = st.text_area(
                "Gefahren für Mensch und Umwelt *",
                value=beispiele.get('gefahren', ''),
                height=150,
                placeholder="Listen Sie die Gefahren auf...",
                key="input_gefahren"
            )
            
            schutzmassnahmen = st.text_area(
                "Schutzmaßnahmen und Verhaltensregeln *",
                value=beispiele.get('schutzmassnahmen', ''),
                height=150,
                placeholder="Beschreiben Sie die Schutzmaßnahmen...",
                key="input_schutzmassnahmen"
            )
            
            stoerungen = st.text_area(
                "Verhalten bei Störungen *",
                value=beispiele.get('stoerungen', ''),
                height=120,
                placeholder="Was ist bei Störungen zu tun?",
                key="input_stoerungen"
            )
            
            unfaelle = st.text_area(
                "Verhalten bei Unfällen / Erste Hilfe *",
                value=beispiele.get('unfaelle', ''),
                height=150,
                placeholder="Erste-Hilfe-Maßnahmen und Notfallverhalten...",
                key="input_unfaelle"
            )
            
            instandhaltung = st.text_area(
                "Instandhaltung *",
                value=beispiele.get('instandhaltung', ''),
                height=120,
                placeholder="Wartung und Instandhaltung...",
                key="input_instandhaltung"
            )
            
            entsorgung = st.text_area(
                "Sachgerechte Entsorgung *",
                value=beispiele.get('entsorgung', ''),
                height=120,
                placeholder="Entsorgungshinweise...",
                key="input_entsorgung"
            )
            
            submitted = st.form_submit_button("📄 PDF erstellen", use_container_width=True)
            
            if submitted:
                if not all([arbeitsbereich, titel, ersteller, anwendungsbereich, gefahren, 
                           schutzmassnahmen, stoerungen, unfaelle, instandhaltung, entsorgung]):
                    st.error("⚠️ Bitte füllen Sie alle Pflichtfelder aus!")
                else:
                    # PDF erstellen
                    data = {
                        'kategorie': kategorie_option,
                        'arbeitsbereich': arbeitsbereich,
                        'titel': titel,
                        'ersteller': ersteller,
                        'anwendungsbereich': anwendungsbereich,
                        'gefahren': gefahren,
                        'schutzmassnahmen': schutzmassnahmen,
                        'stoerungen': stoerungen,
                        'unfaelle': unfaelle,
                        'instandhaltung': instandhaltung,
                        'entsorgung': entsorgung
                    }
                    
                    with st.spinner('PDF wird erstellt...'):
                        pdf_buffer = create_pdf(data)
                        
                    st.success("✅ PDF erfolgreich erstellt!")
                    
                    st.download_button(
                        label="⬇️ PDF herunterladen",
                        data=pdf_buffer,
                        file_name=f"betriebsanweisung_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
