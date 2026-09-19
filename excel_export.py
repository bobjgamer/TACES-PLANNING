import pandas as pd
import io

def generate_excel_model(family_data):
    """
    Generates a full formula-driven Excel model for offline use.
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Formatting
        header = workbook.add_format({'bold': True, 'bg_color': '#2C3E50', 'font_color': 'white', 'border': 1})
        money = workbook.add_format({'num_format': '$#,##0.00'})
        input_fmt = workbook.add_format({'bg_color': '#FFF2CC', 'border': 1}) 
        
        # 1. Inputs Tab
        inputs = workbook.add_worksheet('Family Inputs')
        inputs.write('A1', 'Metric', header)
        inputs.write('B1', 'Spouse 1', header)
        inputs.write('C1', 'Spouse 2', header)
        
        inputs.write('A2', 'Employment Income')
        inputs.write('B2', family_data.get('s1_inc', 0), input_fmt)
        inputs.write('C2', family_data.get('s2_inc', 0), input_fmt)
        
        inputs.write('A3', 'RRSP Contributions')
        inputs.write('B3', family_data.get('s1_rrsp', 0), input_fmt)
        inputs.write('C3', family_data.get('s2_rrsp', 0), input_fmt)

        inputs.write('A4', 'Taxes Withheld')
        inputs.write('B4', family_data.get('s1_withheld', 0), input_fmt)
        inputs.write('C4', family_data.get('s2_withheld', 0), input_fmt)

        # 2. Registered Accounts Tab
        reg = workbook.add_worksheet('Registered Accounts')
        reg.write('A1', 'Account Type', header)
        reg.write('B1', 'Available Room', header)
        reg.write('C1', 'Planned Contribution', header)
        reg.write('A2', 'S1 RRSP')
        reg.write('B2', 20000, input_fmt)
        reg.write('C2', 5000, input_fmt)
        reg.write('A3', 'Child 1 RESP')
        reg.write('B3', 50000, input_fmt)
        reg.write('C3', 2500, input_fmt)

        # 3. Tax Calculator Tab (Formula Driven)
        calc = workbook.add_worksheet('Tax Calculator')
        calc.write('A1', 'Description', header)
        calc.write('B1', 'Spouse 1', header)
        calc.write('C1', 'Spouse 2', header)
        
        calc.write('A2', 'Net Income')
        calc.write_formula('B2', "='Family Inputs'!B2-'Family Inputs'!B3", money)
        calc.write_formula('C2', "='Family Inputs'!C2-'Family Inputs'!C3", money)
        
        calc.write('A3', 'Estimated Tax (Static 25% model for Excel)')
        calc.write_formula('B3', "=B2*0.25", money)
        calc.write_formula('C3', "=C2*0.25", money)
        
        calc.write('A4', 'Refund / (Owing)')
        calc.write_formula('B4', "='Family Inputs'!B4-B3", money)
        calc.write_formula('C4', "='Family Inputs'!C4-C3", money)

    output.seek(0)
    return output
