import plotly.graph_objects as go

# Comparision table to other protocols
def tableCompare(circuit_size, p_time, v_time, memory):
    
    headerColor = 'white'
    rowColor = 'white'

    fig = go.Figure(data=[go.Table(
      header=dict(
        values=['<b>Protocol</b>','<b>libSNARK</b>','<b>This work</b>'],
        line_color='darkslategray',
        fill_color=headerColor,
        align=['center','center'],
        font=dict(color='black', size=12)
      ),
      cells=dict(
        # ordered in column
        values=[
          ['Proof Size', 'Prover Time', 'Verifier Time', 'Memory Used'],
          ['0.13KB', '360s', '0.002s', '\u2265 10GB'],
          [circuit_size+'KB', p_time+'s', v_time+'s', str(memory)+'KB']],
        line_color='darkslategray',
        fill_color=rowColor,
        align = ['center', 'center'],
        font = dict(color = 'black', size = 11)
        ))
    ])

    fig.show()
