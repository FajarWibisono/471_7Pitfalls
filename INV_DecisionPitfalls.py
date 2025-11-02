import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from datetime import date
import random
import io

# Database setup
conn = sqlite3.connect('responses.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    test_date TEXT,
    email TEXT,
    scores TEXT
)
''')
conn.commit()

# Define the 7 pitfalls
pitfalls = [
    "Bounded Rationality (Rasionalitas Terbatas)",
    "Satisficing (Kemudahpuasan)",
    "Hastiness (Ketergesaan)",
    "Group Think (Pemikiran Kelompok)",
    "Group Shift (Pengaruh Posisi)",
    "Decision Dodging (Penundaan Keputusan)",
    "Going Solo (Jalan Sendiri)"
]

# Define tips for each pitfall
tips = [
    "Gunakan pendekatan pemikiran dasar (first principles) untuk memecah masalah menjadi elemen dasar. Terapkan metode ilmiah dengan menguji hipotesis. Gunakan aturan sederhana (heuristics) untuk keputusan cepat sambil berusaha mengumpulkan informasi lebih lengkap.",
    "Sadari kebiasaan memaksimalkan dan putuskan mana keputusan yang benar-benar perlu dioptimalkan. Terima trade-offs dan fokus pada solusi yang cukup baik untuk efisiensi. Buat keputusan kedua tingkat untuk menentukan prioritas.",
    "Buat rutinitas harian untuk mengurangi jumlah keputusan kecil. Jangan ambil keputusan penting saat lapar, marah, kesepian, atau lelah (HALT). Ambil waktu untuk bernapas dalam atau evaluasi opsi secara tenang sebelum memutuskan.",
    "Dorong diskusi terbuka dan berikan agenda rapat sebelumnya agar semua siap berkontribusi. Tunjuk 'devil's advocate' untuk menantang ide mayoritas. Dorong perspektif beragam dan gunakan voting anonim untuk menghindari konformitas.",
    "Evaluasi opini secara independen sebelum diskusi kelompok. Gunakan teknik devil's advocacy untuk mengeksplorasi sudut pandang berlawanan. Sadari pengaruh anggota berpengaruh dan promosikan keseimbangan dalam diskusi.",
    "Tetapkan deadline ketat untuk setiap keputusan agar tidak menunda. Mulai dengan keputusan kecil untuk membangun momentum. Gunakan proses pengambilan keputusan terstruktur seperti daftar pro-kontra untuk mengurangi ketakutan akan konsekuensi.",
    "Konsultasikan dengan orang lain untuk mendapatkan perspektif berbeda. Libatkan tim atau ahli dalam keputusan besar yang memengaruhi banyak pihak. Cari masukan dari pemimpin atau mentor sebelum memutuskan sendirian."
]

# Define 28 questions (4 per pitfall)
# Based on test theory with Edwards' Criterion for item selection to minimize social desirability bias
# Questions are statements where agreement indicates proneness to the pitfall
# Simple language for high school graduates
questions = [
    # Bounded Rationality
    {"text": "Saya sering memutuskan sesuatu tanpa memeriksa semua informasi yang ada.", "pitfall": 0},
    {"text": "Saya biasanya hanya melihat bagian sederhana dari masalah sebelum memilih.", "pitfall": 0},
    {"text": "Saya tidak selalu memikirkan semua kemungkinan saat membuat pilihan.", "pitfall": 0},
    {"text": "Saya cenderung mengabaikan detail rumit saat mengambil keputusan.", "pitfall": 0},
    
    # Satisficing
    {"text": "Saya puas dengan pilihan yang lumayan baik, tidak perlu yang terbaik.", "pitfall": 1},
    {"text": "Saya berhenti mencari jika sudah menemukan sesuatu yang cukup bagus.", "pitfall": 1},
    {"text": "Saya tidak mau repot mencari opsi lebih baik jika yang ada sudah oke.", "pitfall": 1},
    {"text": "Saya sering memilih yang pertama kali terlihat cukup memuaskan.", "pitfall": 1},
    
    # Hastiness
    {"text": "Saya sering terburu-buru memutuskan karena tidak sabar menunggu.", "pitfall": 2},
    {"text": "Saya membuat keputusan cepat saat merasa waktu mendesak.", "pitfall": 2},
    {"text": "Saya cenderung memilih tanpa berpikir panjang karena ingin segera selesai.", "pitfall": 2},
    {"text": "Saya sering mengambil jalan pintas dalam keputusan karena tertekan waktu.", "pitfall": 2},
    
    # Group Think
    {"text": "Saya biasanya setuju dengan pendapat kelompok agar tidak berbeda sendiri.", "pitfall": 3},
    {"text": "Saya ikut saja dengan mayoritas meskipun ragu dengan idenya.", "pitfall": 3},
    {"text": "Saya tidak suka menentang kelompok karena ingin diterima.", "pitfall": 3},
    {"text": "Saya sering mengikuti arus kelompok tanpa mempertanyakan.", "pitfall": 3},
    
    # Group Shift
    {"text": "Pendapat orang berpengaruh sering mengubah cara saya berpikir.", "pitfall": 4},
    {"text": "Saya cenderung bergeser ke posisi ekstrem jika kelompok melakukannya.", "pitfall": 4},
    {"text": "Posisi teman atau atasan sering memengaruhi keputusan saya.", "pitfall": 4},
    {"text": "Saya mudah terbawa oleh opini kuat dari anggota kelompok.", "pitfall": 4},
    
    # Decision Dodging
    {"text": "Saya sering menunda memutuskan karena takut salah.", "pitfall": 5},
    {"text": "Saya menghindari keputusan sulit dengan menunggu lebih lama.", "pitfall": 5},
    {"text": "Saya ragu-ragu mengambil keputusan karena khawatir akibatnya.", "pitfall": 5},
    {"text": "Saya suka menunda pilihan penting sampai terpaksa.", "pitfall": 5},
    
    # Going Solo
    {"text": "Saya lebih suka memutuskan sendiri tanpa bertanya orang lain.", "pitfall": 6},
    {"text": "Saya sering mengambil keputusan sendirian meskipun ada tim.", "pitfall": 6},
    {"text": "Saya tidak perlu masukan dari orang lain untuk memilih.", "pitfall": 6},
    {"text": "Saya biasanya jalan sendiri dalam membuat keputusan besar.", "pitfall": 6}
]

# Likert scale
scale = ["Sangat Tidak Setuju", "Tidak Setuju", "Netral", "Setuju", "Sangat Setuju"]

# Function to calculate scores
def calculate_scores(answers):
    scores = [0] * 7
    counts = [0] * 7
    for i, ans in enumerate(answers):
        pit = questions[i]["pitfall"]
        scores[pit] += ans  # ans is 1 to 5
        counts[pit] += 1
    return [round(scores[i] / counts[i], 2) if counts[i] > 0 else 0 for i in range(7)]

# Function to get interpretation
def get_interpretation(score):
    if score <= 2:
        return "Kecenderungan rendah: Anda jarang terjebak pada jebakan ini. Anda cenderung membuat keputusan dengan mempertimbangkan kompleksitas secara lebih baik."
    elif score <= 3:
        return "Kecenderungan sedang: Anda kadang-kadang terjebak, tetapi masih bisa mengelolanya. Perhatikan situasi di mana ini muncul."
    else:
        return "Kecenderungan tinggi: Anda sering terjebak pada jebakan ini. Disarankan untuk lebih sadar dan mencari strategi untuk menghindarinya."

# Function to generate chart
def generate_chart(scores):
    fig, ax = plt.subplots()
    ax.barh(pitfalls, scores, color='skyblue')
    ax.set_xlabel('Rata-rata Skor (1-5)')
    ax.set_title('Profil Kecenderungan Pitfalls')
    ax.set_xlim(1, 5)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# Streamlit app
st.title("Tes Kecenderungan Pitfalls dalam Pengambilan Keputusan")

# Admin section
if st.sidebar.checkbox("Admin Mode"):
    password = st.sidebar.text_input("Password", type="password")
    if password == "admin234":
        st.sidebar.success("Akses Admin Diberikan")
        # Export data
        df = pd.read_sql_query("SELECT * FROM responses", conn)
        if not df.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            st.sidebar.download_button(
                label="Download Excel",
                data=output,
                file_name="responses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.sidebar.info("Tidak ada data untuk diekspor.")
    else:
        st.sidebar.error("Password salah.")

# Instructions
st.header("Petunjuk Pengisian")
st.write("""
Tes ini untuk mengukur kecenderungan Anda dalam pengambilan keputusan. Ada 28 pernyataan. 
Untuk setiap pernyataan, pilih seberapa setuju Anda dari skala: 
Sangat Tidak Setuju (1), Tidak Setuju (2), Netral (3), Setuju (4), Sangat Setuju (5).

Contoh: 
Pernyataan: "Saya suka makan nasi."
Jika Anda sangat setuju, pilih 'Sangat Setuju'.

Isi dengan jujur. Tidak ada jawaban benar atau salah. 
Waktu pengerjaan sekitar 7 - 10  menit.
""")

# Form
with st.form(key="test_form"):
    name = st.text_input("Nama")
    email = st.text_input("Email")
    test_date = date.today().strftime("%Y-%m-%d")
    st.write(f"Tanggal Tes: {test_date}")
    
    # Shuffle questions
    random.shuffle(questions)
    
    answers = []
    for i, q in enumerate(questions):
        st.subheader(f"Pernyataan {i+1}")
        ans = st.radio(q["text"], scale, index=2, horizontal=True)  # Default netral
        answers.append(scale.index(ans) + 1)  # 1 to 5
    
    submit = st.form_submit_button("Submit")

if submit:
    if not name or not email:
        st.error("Nama dan Email harus diisi.")
    else:
        # Calculate
        scores = calculate_scores(answers)
        
        # Display results as table
        st.header("Hasil Profil Anda")
        results_df = pd.DataFrame({
            "Pitfalls": pitfalls,
            "SKOR": scores,
            "Interpretasi": [get_interpretation(s) for s in scores],
            "Tips Mengurangi": tips
        })
        st.dataframe(
            results_df,
            hide_index=True,
            column_config={
                "Pitfalls": st.column_config.TextColumn(width="large"),
                "SKOR": st.column_config.NumberColumn(width="small"),
                "Interpretasi": st.column_config.TextColumn(width="large"),
                "Tips Mengurangi": st.column_config.TextColumn(width=630)  # Increased width for full text display
            },
            use_container_width=True
        )
        
        # Generate and display chart
        chart_buf = generate_chart(scores)
        st.image(chart_buf)
        
        # Save to DB
        scores_str = ",".join(map(str, scores))
        c.execute("INSERT INTO responses (name, test_date, email, scores) VALUES (?, ?, ?, ?)",
                  (name, test_date, email, scores_str))
        conn.commit()
        st.success("Hasil telah disimpan.")


conn.close()

# Sembunyikan tombol Fork & GitHub di Streamlit Cloud
st.markdown(
    """
    <style>
        /* Sembunyikan tombol Fork dan ikon GitHub */
        .stApp [data-testid="stHeader"] {
            display: none !important;
        }
        /* Jika ingin sembunyikan juga menu 3 titik (More options) */
        .stApp [data-testid="stToolbar"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

