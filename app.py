import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime

# Configuración de la base de datos
DB_HOST = "ep-fancy-water-a8wxz1l5.eastus2.azure.neon.tech"
DB_NAME = "megatoys"
DB_USER = "megatoys_owner"
DB_PASSWORD = "Frd9KtLl3zvx"

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

												   
@st.cache_data(ttl=1)
def load_data():
    conn = connect_db()
    if conn:
        try:
            query = """
                SELECT id_empleado, nombre, 
                       NULLIF(TRIM(nro_factura), '') as nro_factura,
                       fecha, 
                       valor,
                       tipo_venta
                FROM empleados;
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            conn.close()
            return pd.DataFrame(columns=["id_empleado", "nombre", "nro_factura", "fecha", "valor", "tipo_venta"])
    return pd.DataFrame(columns=["id_empleado", "nombre", "nro_factura", "fecha", "valor", "tipo_venta"])

def check_existing_invoice(cursor, nro_factura):
    query = "SELECT id_empleado FROM empleados WHERE nro_factura = %s;"
    cursor.execute(query, (nro_factura,))
    return cursor.fetchone() is not None

def save_data(id_empleado, nombre, nro_factura, valor, tipo_venta):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Verificar si el número de factura ya existe
            if check_existing_invoice(cursor, nro_factura):
                st.error("Este número de factura ya está asignado a otro empleado.")
                conn.close()
                return False

            # Verificar el estado actual del empleado
            cursor.execute(
                "SELECT nro_factura FROM empleados WHERE id_empleado = %s;",
                (id_empleado,)
            )
            result = cursor.fetchone()
            
            # Convertir explícitamente None o cadena vacía a None
            current_invoice = result[0] if result and result[0] and str(result[0]).strip() else None

            if current_invoice:
                st.error("El empleado ya tiene un número de factura asignado.")
                conn.close()
                return False

            # Convertir el valor a numeric o None si está vacío
            valor_numeric = None
            if valor and valor.strip():
                try:
                    valor_numeric = float(valor.replace(',', '').strip())
                except ValueError:
                    st.error("El valor debe ser un número válido")
                    conn.close()
                    return False

            # Actualizar los campos
            query_update = """
            UPDATE empleados
            SET nro_factura = %s, 
                fecha = %s, 
                valor = %s,
                tipo_venta = %s
            WHERE id_empleado = %s;
            """
            cursor.execute(query_update, (nro_factura, datetime.now(), valor_numeric, tipo_venta, id_empleado))
            conn.commit()
            st.success("Datos actualizados correctamente.")
            
            # Limpiar el caché después de guardar
            st.cache_data.clear()
            
            conn.close()
            return True
            
        except Exception as e:
            st.error(f"Error al guardar datos: {e}")
            conn.close()
            return False

def main():
    st.title("Formulario de Validación de Empleados")

    df = load_data()

    id_empleado = st.text_input("Ingrese el ID del empleado:")

    if id_empleado:
        empleado = df[df["id_empleado"] == id_empleado]

        if not empleado.empty:
            nombre_empleado = empleado.iloc[0]["nombre"]
            st.success(f"Empleado encontrado: {nombre_empleado}")

            # Mostrar estado actual
            factura_actual = empleado.iloc[0]["nro_factura"]
            
            if pd.isna(factura_actual) or factura_actual is None or str(factura_actual).strip() == '':
                st.info("Este empleado no tiene factura asignada.")
				 
															
                
                # Solo mostrar los campos si no tiene factura
                nro_factura = st.text_input("Ingrese el número de factura (obligatorio):")
                valor_factura = st.text_input("Ingrese el valor de la factura (obligatorio):")
                tipo_venta = st.selectbox("Seleccione el tipo de venta", ["Contado", "Crédito"])

                if st.button("Guardar"):
                    if not nro_factura or not nro_factura.strip():
                        st.error("El número de factura es obligatorio.")
                    elif not valor_factura or not valor_factura.strip():
                        st.error("El valor de la factura es obligatorio.")
                    else:
                        save_data(id_empleado, nombre_empleado, nro_factura, valor_factura, tipo_venta)
															
                        st.rerun()
            else:
                st.info(f"Factura actual: {factura_actual}")
                valor_actual = empleado.iloc[0]["valor"]
                tipo_venta_actual = empleado.iloc[0]["tipo_venta"] or "No especificado"
                st.info(f"Valor: ${valor_actual:,.2f}")
                st.info(f"Tipo de venta: {tipo_venta_actual}")
        else:
            st.error("ID de empleado no encontrado.")

if __name__ == "__main__":
    main()