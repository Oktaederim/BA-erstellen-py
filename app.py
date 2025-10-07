# app.py
from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import io
import os

app = Flask(__name__)

# Vorlagen für verschiedene Betriebsanweisungskategorien
VORLAGEN = {
    "maschine": {
        "name": "Maschinen und Anlagen",
        "farbe": colors.HexColor("#FF6B35"),
        "icon": "⚙️",
        "beispiele": {
            "anwendungsbereich": "Bedienung der CNC-Fräsmaschine im Produktionsbereich",
            "gefahren": "• Quetschgefahr durch bewegliche Maschinenteile\n• Verletzungsgefahr durch Späne\n• Lärmbelastung",
            "schutzmassnahmen": "• Schutzeinrichtungen dürfen nicht entfernt werden\n• Gehörschutz und Schutzbrille tragen\n• Lange Haare zusammenbinden\n• Keine weite Kleidung tragen",
            "stoerungen": "• Maschine sofort ausschalten (NOT-AUS)\n• Vorgesetzten informieren\n• Nicht selbst reparieren",
            "unfaelle": "• Verletzte Person aus dem Gefahrenbereich bringen\n• Erste Hilfe leisten\n• Notruf 112\n• Durchgangsarzt kontaktieren",
            "instandhaltung": "• Nur durch befugte Personen\n• Maschine vor Wartung ausschalten und gegen Wiedereinschalten sichern\n• Wartungsplan beachten",
            "entsorgung": "• Späne in vorgesehenen Behältern sammeln\n• Kühlschmierstoffe ordnungsgemäß entsorgen"
        }
    },
    "gefahrstoff": {
        "name": "Gefahrstoffe",
        "farbe": colors.HexColor("#E63946"),
        "icon": "☠️",
        "beispiele": {
            "anwendungsbereich": "Umgang mit Lösungsmitteln in der Lackiererei",
            "gefahren": "• Gesundheitsschädlich bei Einatmen\n• Reizend für Augen und Haut\n• Leichtentzündlich\n• Umweltgefährdend",
            "schutzmassnahmen": "• Nur in gut belüfteten Räumen verwenden\n• Atemschutz, Schutzhandschuhe und Schutzbrille tragen\n• Von Zündquellen fernhalten\n• Nicht rauchen\n• Hautkontakt vermeiden",
            "stoerungen": "• Bei Verschütten: Räumlichkeit lüften\n• Mit Bindemittel aufnehmen\n• Zündquellen entfernen\n• Vorgesetzten informieren",
            "unfaelle": "• Bei Hautkontakt: Sofort mit viel Wasser abwaschen\n• Bei Augenkontakt: 15 Minuten mit Wasser spülen, Arzt aufsuchen\n• Bei Einatmen: An die frische Luft, Arzt konsultieren\n• Notruf 112 bei schweren Vergiftungen",
            "instandhaltung": "• Behälter dicht verschlossen halten\n• Regelmäßige Kontrolle der Lagerbedingungen\n• Absauganlage warten",
            "entsorgung": "• Nicht in Ausguss oder Mülltonne\n• In gekennzeichneten Behältern sammeln\n• Durch Fachfirma entsorgen lassen"
        }
    },
    "taetigkeit": {
        "name": "Tätigkeiten",
        "farbe": colors.HexColor("#457B9D"),
        "icon": "👷",
        "beispiele": {
            "anwendungsbereich": "Arbeiten auf Leitern und Gerüsten",
            "gefahren": "• Absturzgefahr aus der Höhe\n• Umkippen der Leiter\n• Herabfallende Gegenstände",
            "schutzmassnahmen": "• Nur geprüfte Leitern verwenden\n• Leiter auf festem, ebenen Untergrund aufstellen\n• Anlegewinkel von 65-75° einhalten\n• Nicht auf obersten zwei Sprossen stehen\n• Absturzsicherung ab 2m Höhe\n• Arbeitsbereich absperren",
            "stoerungen": "• Bei beschädigter Leiter: Nicht verwenden, kennzeichnen\n• Vorgesetzten informieren\n• Leiter außer Betrieb nehmen",
            "unfaelle": "• Notruf 112\n• Erste Hilfe leisten\n• Verletzte Person nicht bewegen bei Verdacht auf Wirbelsäulenverletzung\n• Unfallstelle sichern",
            "instandhaltung": "• Regelmäßige Sichtprüfung vor Benutzung\n• Jährliche Prüfung durch befähigte Person\n• Leitern trocken lagern",
            "entsorgung": "• Defekte Leitern fachgerecht entsorgen\n• Nicht reparieren lassen"
        }
    },
    "biologisch": {
        "name": "Biologische Arbeitsstoffe",
        "farbe": colors.HexColor("#2A9D8F"),
        "icon": "🦠",
        "beispiele": {
            "anwendungsbereich": "Umgang mit biologischen Arbeitsstoffen im Labor",
            "gefahren": "• Infektionsgefahr durch Krankheitserreger\n• Allergische Reaktionen\n• Kontamination",
            "schutzmassnahmen": "• Laborkittel, Handschuhe und ggf. Atemschutz tragen\n• Hygienemaßnahmen strikt einhalten\n• Hände desinfizieren\n• Nicht essen, trinken oder rauchen\n• Arbeiten in Sicherheitswerkbank",
            "stoerungen": "• Bei Kontamination: Bereich absperren\n• Desinfektion durchführen\n• Biologischen Sicherheitsbeauftragten informieren",
            "unfaelle": "• Bei Verletzung: Wunde bluten lassen, desinfizieren\n• Betriebsarzt aufsuchen\n• Durchgangsarzt bei schweren Verletzungen\n• Vorfall dokumentieren",
            "instandhaltung": "• Regelmäßige Wartung der Sicherheitswerkbank\n• Autoklavierung von Geräten\n• Dekontamination der Arbeitsflächen",
            "entsorgung": "• Autoklavierung von kontaminierten Materialien\n• Entsorgung in speziellen Biohazard-Behältern\n• Durch Fachfirma entsorgen lassen"
        }
    }
}

@app.route('/')
def index():
    return render_template('index.html', vorlagen=VORLAGEN)

@app.route('/api/vorlagen')
def get_vorlagen():
    return jsonify(VORLAGEN)

@app.route('/api/erstellen', methods=['POST'])
def erstellen():
    data = request.json
    
    # PDF erstellen
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Styles
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
    
    # Story für PDF
    story = []
    
    # Header mit Kategorie-Farbe
    kategorie = data.get('kategorie', 'taetigkeit')
    farbe = VORLAGEN[kategorie]['farbe']
    
    # Titel
    story.append(Paragraph("BETRIEBSANWEISUNG", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Info-Tabelle
    info_data = [
        ["Arbeitsbereich:", data.get('arbeitsbereich', '')],
        ["Tätigkeit/Maschine:", data.get('titel', '')],
        ["Erstellt am:", datetime.now().strftime("%d.%m.%Y")],
        ["Erstellt von:", data.get('ersteller', '')]
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
        ("1. ANWENDUNGSBEREICH", data.get('anwendungsbereich', '')),
        ("2. GEFAHREN FÜR MENSCH UND UMWELT", data.get('gefahren', '')),
        ("3. SCHUTZMAßNAHMEN UND VERHALTENSREGELN", data.get('schutzmassnahmen', '')),
        ("4. VERHALTEN BEI STÖRUNGEN", data.get('stoerungen', '')),
        ("5. VERHALTEN BEI UNFÄLLEN / ERSTE HILFE", data.get('unfaelle', '')),
        ("6. INSTANDHALTUNG / ENTSORGUNG", data.get('instandhaltung', '') + "\n\n" + data.get('entsorgung', ''))
    ]
    
    for titel, inhalt in abschnitte:
        # Überschrift mit farbigem Hintergrund
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
        
        # Inhalt
        if inhalt:
            # Text formatieren (Zeilenumbrüche beibehalten)
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
    
    # PDF bauen
    doc.build(story)
    
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'betriebsanweisung_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

if __name__ == '__main__':
    # Templates-Verzeichnis erstellen
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # HTML-Template erstellen
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE)
    
    app.run(debug=True, port=5000)

# HTML Template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Betriebsanweisungs-Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .vorlagen {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .vorlage-card {
            background: #f8f9fa;
            border: 3px solid transparent;
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }
        
        .vorlage-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .vorlage-card.active {
            border-color: #667eea;
            background: #f0f4ff;
        }
        
        .vorlage-icon {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        .vorlage-name {
            font-weight: bold;
            color: #333;
        }
        
        .form-section {
            margin-bottom: 25px;
        }
        
        .form-section label {
            display: block;
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
            font-size: 0.95em;
        }
        
        .form-section input,
        .form-section textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        
        .form-section input:focus,
        .form-section textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-section textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        
        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-beispiel {
            background: #28a745;
            color: white;
        }
        
        .btn-beispiel:hover {
            background: #218838;
        }
        
        .section-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        
        .hinweis {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 25px;
            border-radius: 5px;
        }
        
        .hinweis strong {
            color: #856404;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .container {
                border-radius: 0;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
            
            .content {
                padding: 20px;
            }
            
            .vorlagen {
                grid-template-columns: 1fr;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Betriebsanweisungs-Generator</h1>
            <p>Erstellen Sie professionelle Betriebsanweisungen für Ihre Arbeitssicherheit</p>
        </div>
        
        <div class="content">
            <div class="hinweis">
                <strong>Hinweis:</strong> Betriebsanweisungen sind wichtige Dokumente für die Arbeitssicherheit. 
                Bitte prüfen Sie alle Angaben sorgfältig und passen Sie sie an Ihre spezifischen Anforderungen an.
            </div>
            
            <h2 class="section-title">1. Kategorie wählen</h2>
            <div class="vorlagen" id="vorlagen">
                {% for key, vorlage in vorlagen.items() %}
                <div class="vorlage-card" data-kategorie="{{ key }}" onclick="selectVorlage('{{ key }}')">
                    <div class="vorlage-icon">{{ vorlage.icon }}</div>
                    <div class="vorlage-name">{{ vorlage.name }}</div>
                </div>
                {% endfor %}
            </div>
            
            <h2 class="section-title">2. Angaben eingeben</h2>
            
            <form id="betriebsanweisungForm">
                <input type="hidden" id="kategorie" name="kategorie" value="taetigkeit">
                
                <div class="form-section">
                    <label for="arbeitsbereich">Arbeitsbereich / Abteilung *</label>
                    <input type="text" id="arbeitsbereich" name="arbeitsbereich" required 
                           placeholder="z.B. Produktionshalle 2, Werkstatt, Labor">
                </div>
                
                <div class="form-section">
                    <label for="titel">Tätigkeit / Maschine / Gefahrstoff *</label>
                    <input type="text" id="titel" name="titel" required 
                           placeholder="z.B. CNC-Fräsmaschine, Lösungsmittel, Leiterarbeiten">
                </div>
                
                <div class="form-section">
                    <label for="ersteller">Erstellt von *</label>
                    <input type="text" id="ersteller" name="ersteller" required 
                           placeholder="Ihr Name">
                </div>
                
                <div class="form-section">
                    <label for="anwendungsbereich">Anwendungsbereich *</label>
                    <textarea id="anwendungsbereich" name="anwendungsbereich" required 
                              placeholder="Beschreiben Sie den Anwendungsbereich..."></textarea>
                </div>
                
                <div class="form-section">
                    <label for="gefahren">Gefahren für Mensch und Umwelt *</label>
                    <textarea id="gefahren" name="gefahren" required 
                              placeholder="Listen Sie die Gefahren auf..."></textarea>
                </div>
                
                <div class="form-section">
                    <label for="schutzmassnahmen">Schutzmaßnahmen und Verhaltensregeln *</label>
                    <textarea id="schutzmassnahmen" name="schutzmassnahmen" required 
                              placeholder="Beschreiben Sie die Schutzmaßnahmen..."></textarea>
                </div>
                
                <div class="form-section">
                    <label for="stoerungen">Verhalten bei Störungen *</label>
                    <textarea id="stoerungen" name="stoerungen" required 
                              placeholder="Was ist bei Störungen zu tun?"></textarea>
                </div>
                
                <div class="form-section">
                    <label for="unfaelle">Verhalten bei Unfällen / Erste Hilfe *</label>
                    <textarea id="unfaelle" name="unfaelle" required 
                              placeholder="Erste-Hilfe-Maßnahmen und Notfallverhalten..."></textarea>
                </div>
                
                <div class="form-section">
                    <label for="instandhaltung">Instandhaltung *</label>
                    <textarea id="instandhaltung" name="instandhaltung" required 
                              placeholder="Wartung und Instandhaltung..."></textarea>
                </div>
                
                <div class="form-section">
                    <label for="entsorgung">Sachgerechte Entsorgung *</label>
                    <textarea id="entsorgung" name="entsorgung" required 
                              placeholder="Entsorgungshinweise..."></textarea>
                </div>
                
                <div class="button-group">
                    <button type="button" class="btn-beispiel" onclick="fillBeispiel()">
                        📋 Beispiel laden
                    </button>
                    <button type="button" class="btn-secondary" onclick="resetForm()">
                        🔄 Zurücksetzen
                    </button>
                    <button type="submit" class="btn-primary">
                        📄 PDF erstellen
                    </button>
                </div>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>PDF wird erstellt...</p>
            </div>
        </div>
    </div>
    
    <script>
        let vorlagen = {{ vorlagen | tojson }};
        let selectedKategorie = 'taetigkeit';
        
        function selectVorlage(kategorie) {
            // Alte Auswahl entfernen
            document.querySelectorAll('.vorlage-card').forEach(card => {
                card.classList.remove('active');
            });
            
            // Neue Auswahl markieren
            document.querySelector(`[data-kategorie="${kategorie}"]`).classList.add('active');
            
            selectedKategorie = kategorie;
            document.getElementById('kategorie').value = kategorie;
        }
        
        function fillBeispiel() {
            const beispiele = vorlagen[selectedKategorie].beispiele;
            
            document.getElementById('anwendungsbereich').value = beispiele.anwendungsbereich;
            document.getElementById('gefahren').value = beispiele.gefahren;
            document.getElementById('schutzmassnahmen').value = beispiele.schutzmassnahmen;
            document.getElementById('stoerungen').value = beispiele.stoerungen;
            document.getElementById('unfaelle').value = beispiele.unfaelle;
            document.getElementById('instandhaltung').value = beispiele.instandhaltung;
            document.getElementById('entsorgung').value = beispiele.entsorgung;
        }
        
        function resetForm() {
            if (confirm('Möchten Sie wirklich alle Eingaben zurücksetzen?')) {
                document.getElementById('betriebsanweisungForm').reset();
            }
        }
        
        document.getElementById('betriebsanweisungForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                kategorie: document.getElementById('kategorie').value,
                arbeitsbereich: document.getElementById('arbeitsbereich').value,
                titel: document.getElementById('titel').value,
                ersteller: document.getElementById('ersteller').value,
                anwendungsbereich: document.getElementById('anwendungsbereich').value,
                gefahren: document.getElementById('gefahren').value,
                schutzmassnahmen: document.getElementById('schutzmassnahmen').value,
                stoerungen: document.getElementById('stoerungen').value,
                unfaelle: document.getElementById('unfaelle').value,
                instandhaltung: document.getElementById('instandhaltung').value,
                entsorgung: document.getElementById('entsorgung').value
            };
            
            // Loading anzeigen
            document.getElementById('loading').classList.add('active');
            
            try {
                const response = await fetch('/api/erstellen', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `betriebsanweisung_${new Date().getTime()}.pdf`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    alert('Fehler beim Erstellen des PDFs');
                }
            } catch (error) {
                console.error('Fehler:', error);
                alert('Ein Fehler ist aufgetreten');
            } finally {
                document.getElementById('loading').classList.remove('active');
            }
        });
        
        // Erste Vorlage standardmäßig auswählen
        selectVorlage('taetigkeit');
    </script>
</body>
</html>'''
