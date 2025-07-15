from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load dataset
df = pd.read_csv('eamcet_2024.csv')
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('\n', '_')

# Rename for consistency
df = df.rename(columns={
    'institute_name': 'institute',
    'branch_name': 'branch'
})

# Filter needed columns (edit as per your data)
required_columns = [
    'institute', 'place', 'branch',
    'oc_boys', 'oc_girls',
    'bc_a_boys', 'bc_a_girls',
    'bc_b_boys', 'bc_b_girls',
    'bc_c_boys', 'bc_c_girls',
    'bc_d_boys', 'bc_d_girls',
    'bc_e_boys', 'bc_e_girls',
    'sc_boys', 'sc_girls',
    'st_boys', 'st_girls',
    'ews_gen_ou', 'ews_girls_ou'
]
df = df[required_columns]

# Get unique places
places = sorted(df['place'].dropna().unique().tolist())

@app.route('/')
def index():
    return render_template('index.html', places=places)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            rank = int(request.form['rank'])
            caste = request.form['caste'].lower()
            gender = request.form['gender'].lower()
            branch = request.form['branch'].lower()
            num_colleges = int(request.form['num_colleges'])
            selected_places = request.form.getlist('selected_places')

            # Determine cutoff column
            if caste == "ews":
                col_name = "ews_gen_ou" if gender == "male" else "ews_girls_ou"
            else:
                col_name = f"{caste}_{'boys' if gender == 'male' else 'girls'}"

            if col_name not in df.columns:
                return render_template("result.html", error=f"Invalid caste/gender: {col_name}")

            branch_col = df['branch'].astype(str).str.lower()

            # Apply filters
            filtered = df[
                (branch_col == branch) &
                (pd.to_numeric(df[col_name], errors='coerce') >= rank)
            ]

            if selected_places:
                filtered = filtered[filtered['place'].isin(selected_places)]

            filtered = filtered.sort_values(by=col_name).head(num_colleges)

            if filtered.empty:
                return render_template("result.html", error="No eligible colleges found.")

            result_data = filtered[['institute', 'place', 'branch', col_name]].to_dict(orient='records')
            return render_template("result.html", tables=result_data, rank_col=col_name)

        except Exception as e:
            return render_template("result.html", error=f"Error occurred: {str(e)}")

    # GET fallback
    return render_template('index.html', places=places)

if __name__ == '__main__':
    app.run(debug=True)
