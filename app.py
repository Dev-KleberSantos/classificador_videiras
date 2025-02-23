import streamlit as st
import io
from PIL import Image
import numpy as np
import tensorflow as tf
import plotly.express as px
import gdown

@st.cache_resource
def carrega_modelo():

    #https://drive.google.com/file/d/14u1k-6qte4N_mpbIsjTJqVa0YVsLJZo8/view?usp=drive_link
    url='https://drive.google.com/file/d/14u1k-6qte4N_mpbIsjTJqVa0YVsLJZo8'
    gdown.download(url, 'modelo_quantizado16bits.tflite')
    interpreter = tf.lite.Interpreter(model_path='modelo_quantizado16bits.tflite')
    interpreter.allocate_tensors()
    return interpreter

def carrega_imagem():
    uploaded_file = st.file_uploader('Arraste e solte uma imagem aqui ou clique para selecionar uma', type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))

        st.image(image)
        st.success('Imagem foi carregada com sucesso')

        image = np.array(image, dtype=np.float32)
        image = image / 255.0
        image = np.expand_dims(image, axis=0)

        return image

def previsao(interpreter,image):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    interpreter.set_tensor(input_details[0]['index'],imagem) 
    
    interpreter.invoke()
    
    output_data = interpreter.get_tensor(output_details[0]['index'])
    classes = ['BlackMeasles', 'BlackRot', 'HealthyGrapes', 'LeafBlight']

    df = pd.DataFrame()
    df['classes'] = classes
    df['probabilidades (%)'] = 100*output_data[0]
    
    fig = px.bar(df, y='classes', x='probabilidades (%)', orientation='h', text='probabilidades (%)',
             title='Probabilidade de Classes de Doenças em Uvas')
    st.plotly_chart(fig)



def main():
    st.set_page_config(
        page_title="Classifica Folhas de Videira",
        page_icon="��",
    )

    st.write("# Classifica Folhas de Videira! ��")

    #Carrega modelo
    interpreter = carrega_modelo()
    #Carrega imagem
    image = carrega_imagem()
    #Classifica
    previsao(interpreter,image)

if __name__== 'main':
    main()