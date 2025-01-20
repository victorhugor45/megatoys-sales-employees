import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar el archivo Excel
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("empleados.xlsx", dtype={"ID Empleado": str})
        st.write("Datos cargados correctamente:")  # Mensaje de depuración
        st.write(df)  # Mostrar el DataFrame en la interfaz
    except FileNotFoundError:
        # Si el archivo no existe, crea uno nuevo con las columnas necesarias
        df = pd.DataFrame(columns=["ID Empleado", "Nombre", "Nro factura", "Fecha", "Valor"])
        df.to_excel("empleados.xlsx", index=False)
    return df

def save_data(df):
    df.to_excel("empleados.xlsx", index=False)

def main():
    st.title("Formulario de Validación de Empleados")

    # Cargar datos
    df = load_data()

    # Formulario para ingresar el ID del empleado
    id_empleado = st.text_input("Ingrese el ID del empleado:")

    if id_empleado:
        # Validar si el ID existe en la base de datos
        empleado = df[df["ID Empleado"] == id_empleado]

        if not empleado.empty:
            nombre_empleado = empleado.iloc[0]["Nombre"]
            st.success(f"Empleado encontrado: {nombre_empleado}")

            # Formulario para ingresar el número de factura y el valor
            nro_factura = st.text_input("Ingrese el número de factura (obligatorio):")
            valor_factura = st.text_input("Ingrese el valor de la factura (opcional):")

            if st.button("Guardar"):
                if nro_factura:
                    # Validar si el número de factura ya existe
                    if pd.isna(empleado.iloc[0]["Nro factura"]):
                        # Actualizar el DataFrame
                        df.loc[df["ID Empleado"] == id_empleado, "Nro factura"] = nro_factura
                        df.loc[df["ID Empleado"] == id_empleado, "Fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if valor_factura:
                            df.loc[df["ID Empleado"] == id_empleado, "Valor"] = valor_factura

                        # Guardar los cambios en el archivo Excel
                        save_data(df)
                        st.success("Datos guardados correctamente.")
                    else:
                        st.error("El empleado ya tiene un número de factura asignado.")
                else:
                    st.error("El número de factura es obligatorio.")
        else:
            st.error("ID de empleado no encontrado.")

if __name__ == "__main__":
    main()