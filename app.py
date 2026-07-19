from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np

app = Flask(__name__)

# ===== FUNGSI TOPSIS + SIMPAN STEP =====
def topsis_steps(df, weights, benefit):
    data = df.iloc[:, 1:].values

    # 1. Normalisasi
    norm = data / np.sqrt((data**2).sum(axis=0))
    norm_df = pd.DataFrame(norm, columns=df.columns[1:])

    # 2. Pembobotan
    weighted = norm * weights
    weighted_df = pd.DataFrame(weighted, columns=df.columns[1:])

    # 3. Solusi ideal
    ideal_pos = np.max(weighted, axis=0)
    ideal_neg = np.min(weighted, axis=0)

    for i in range(len(benefit)):
        if benefit[i] == 0:
            ideal_pos[i], ideal_neg[i] = ideal_neg[i], ideal_pos[i]

    # 4. Jarak
    d_pos = np.sqrt(((weighted - ideal_pos)**2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_neg)**2).sum(axis=1))

    # 5. Skor
    score = d_neg / (d_pos + d_neg)

    result = df.copy()
    result['D+'] = d_pos
    result['D-'] = d_neg
    result['Score'] = score
    result['Ranking'] = result['Score'].rank(ascending=False)

    return {
        "norm": norm_df,
        "weighted": weighted_df,
        "result": result.sort_values(by='Score', ascending=False)
    }


# ===== HALAMAN UTAMA =====
@app.route('/', methods=['GET', 'POST'])
def index():
    df = pd.read_csv('dataset_tpa_topsis.csv')

    hasil = None

    if request.method == 'POST':
        weights = [
            float(request.form['w1']),
            float(request.form['w2']),
            float(request.form['w3']),
            float(request.form['w4']),
            float(request.form['w5']),
        ]

        benefit = [0, 0, 1, 1, 0]

        hasil = topsis_steps(df, weights, benefit)

    return render_template(
        'index.html',
        data=df.to_html(classes='table table-bordered', index=False),
        norm=hasil['norm'].to_html(classes='table table-bordered') if hasil else None,
        weighted=hasil['weighted'].to_html(classes='table table-bordered') if hasil else None,
        result=hasil['result'].to_html(classes='table table-bordered') if hasil else None
    )


# ===== TAMBAH DATA =====
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        new_data = {
            "Lokasi": request.form['lokasi'],
            "Jarak_Pemukiman_km": float(request.form['jp']),
            "Jarak_SumberAir_km": float(request.form['js']),
            "Jenis_Tanah_Skor": float(request.form['tanah']),
            "Akses_Jalan_Skor": float(request.form['akses']),
            "Biaya_Lahan_Juta": float(request.form['biaya']),
        }

        df = pd.read_csv('dataset_tpa_topsis.csv')
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv('dataset_tpa_topsis.csv', index=False)

        return redirect(url_for('index'))

    return render_template('tambah_data.html')


if __name__ == '__main__':
    app.run(debug=True)
