import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# Configuración de la base de datos (usando Neon.tech)
DB_HOST = "ep-fancy-water-a8wxz1l5.eastus2.azure.neon.tech"  # Reemplaza con tu host
DB_NAME = "megatoys"  # Nombre de la base de datos
DB_USER = "megatoys_owner"  # Reemplaza con tu usuario
DB_PASSWORD = "Frd9KtLl3zvx"  # Reemplaza con tu contraseña

# Conectar a PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# Cargar datos desde PostgreSQL
@st.cache_data
def load_data():
    conn = connect_db()
    if conn:
        try:
            query = "SELECT id_empleado, nombre, nro_factura, fecha, valor FROM empleados;"
            df = pd.read_sql(query, conn)
            conn.close()
            # Convertir valores vacíos a None
            df["nro_factura"] = df["nro_factura"].replace("", None)
            df["nro_factura"] = df["nro_factura"].where(pd.notnull(df["nro_factura"]), None)
            # Asegurarse de que los valores NULL se manejen correctamente
            df["nro_factura"] = df["nro_factura"].where(pd.notnull(df["nro_factura"]), None)
            # Imprimir el DataFrame para depuración
            st.write("DataFrame cargado desde la base de datos:")
            st.write(df)
            return df
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            conn.close()
            return pd.DataFrame(columns=["id_empleado", "nombre", "nro_factura", "fecha", "valor"])
    else:
        return pd.DataFrame(columns=["id_empleado", "nombre", "nro_factura", "fecha", "valor"])

# Guardar datos en PostgreSQL
def save_data(id_empleado, nombre, nro_factura, valor):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar si el empleado ya tiene un número de factura asignado
            query_check = "SELECT nro_factura FROM empleados WHERE id_empleado = %s;"
            cursor.execute(query_check, (id_empleado,))
            result = cursor.fetchone()

            if result and result[0] is not None:
                st.error("El empleado ya tiene un número de factura asignado.")
            else:
                # Actualizar los campos nro_factura, fecha y valor
                query_update = """
                UPDATE empleados
                SET nro_factura = %s, fecha = %s, valor = %s
                WHERE id_empleado = %s;
                """
                cursor.execute(query_update, (nro_factura, datetime.now(), valor, id_empleado))
                conn.commit()
                st.success("Datos actualizados correctamente.")
            conn.close()
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
            conn.close()

def main():
    st.title("Formulario de Validación de Empleados")

    # Cargar datos
    df = load_data()

    # Formulario para ingresar el ID del empleado
    id_empleado = st.text_input("Ingrese el ID del empleado:")

    if id_empleado:
        # Validar si el ID existe en la base de datos
        empleado = df[df["id_empleado"] == id_empleado]

        if not empleado.empty:
            nombre_empleado = empleado.iloc[0]["nombre"]
            st.success(f"Empleado encontrado: {nombre_empleado}")

            # Formulario para ingresar el número de factura y el valor
            nro_factura = st.text_input("Ingrese el número de factura (obligatorio):")
            valor_factura = st.text_input("Ingrese el valor de la factura (opcional):")

            if st.button("Guardar"):
                if nro_factura:
                    # Verificar si el número de factura ya está asignado
                    if empleado.iloc[0]["nro_factura"] is None:
                        save_data(id_empleado, nombre_empleado, nro_factura, valor_factura)
                    else:
                        st.error("El empleado ya tiene un número de factura asignado.")
                else:
                    st.error("El número de factura es obligatorio.")
        else:
            st.error("ID de empleado no encontrado.")

if __name__ == "__main__":
    main()