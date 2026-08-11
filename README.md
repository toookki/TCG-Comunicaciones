# TCG Comunicaciones - Sistema de Gestión

Este repositorio contiene el código fuente de TCG Comunicaciones, una plataforma cliente-servidor desarrollada íntegramente en Python mediante el uso de sockets. El sistema permite la interacción concurrente de múltiples usuarios clasificados en clientes y ejecutivos, facilitando operaciones de atención, ventas y gestión de inventario.

## Características Principales

*   **Arquitectura Cliente-Servidor Multihilo**: Capacidad para manejar múltiples conexiones simultáneas sin bloqueo gracias al uso de la librería estándar `threading`.
*   **Autenticación Robusta**: Integración de contraseñas y un sistema de Autenticación de Dos Factores (2FA) utilizando `pyotp` y códigos QR.
*   **Roles de Usuario Diferenciados**: Lógicas de interacción separadas para clientes (compras, consultas) y ejecutivos (atención, gestión de órdenes).
*   **Persistencia de Datos**: Sistema de persistencia basado en archivos JSON para catálogos, depósitos, ejecutivos, órdenes, usuarios y bodegas, permitiendo facilidad de migración e inspección.

## Requisitos del Sistema

*   Python 3.8 o superior.
*   Dependencias de terceros especificadas en el archivo de requerimientos.

## Instalación y Configuración

1.  **Clonar el repositorio** e ingresar al directorio principal del proyecto desde su terminal.
2.  **Instalar las dependencias necesarias** ejecutando el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```

## Guía de Uso para Nuevos Usuarios

Para iniciar el sistema de manera correcta, es indispensable levantar primero el servidor y posteriormente conectar las instancias de clientes necesarias.

1.  **Iniciar el Servidor**:
    Desde la raíz del proyecto, ejecute el siguiente comando para levantar el servidor y comenzar a escuchar conexiones entrantes:
    ```bash
    python server/server.py
    ```
    El servidor comenzará a ejecutarse y la consola indicará que se encuentra a la espera de clientes.

2.  **Iniciar el Cliente**:
    Abra una nueva terminal, asegúrese de estar en la raíz del proyecto, y ejecute:
    ```bash
    python user/user.py
    ```
    Al conectar, el sistema le consultará su tipo de usuario. Debe ingresar `client` para acceder como usuario regular, o `executive` para acceder como ejecutivo.
    
    *Nota de Seguridad:* Si accede como ejecutivo y tiene la autenticación de dos factores (2FA) habilitada, necesitará escanear su código QR (ubicado en la carpeta `qr_codes/`) mediante una aplicación compatible como Google Authenticator o Authy para obtener el token temporal.

## Funcionalidades del Sistema

Una vez autenticado exitosamente, la interacción dependerá de su rol seleccionado.

### Interfaz de Cliente (Client)
Los clientes interactúan mediante un menú numérico. Al ingresar el número de una opción, el sistema solicita los datos necesarios para completar la transacción. Las principales opciones incluyen:
*   **Soporte Técnico**: Solicitud de atención con un ejecutivo disponible para abrir un chat directo.
*   **Consultar Saldo y Depositar**: Revisión de los fondos actuales en cuenta y solicitud de cargas de dinero.
*   **Catálogo y Compras**: Exploración del catálogo de cartas publicadas y generación de órdenes de compra.
*   **Gestión de Órdenes**: Confirmación de la recepción de envíos o solicitud de devoluciones.

### Interfaz de Ejecutivo (Executive)
Los ejecutivos operan a través de una consola mediante comandos que inician con el caracter dos puntos (`:`).
*   **Atención al Cliente**:
    *   `:status` / `:details`: Verifica cuántos clientes hay en espera y permite revisar su historial.
    *   `:connect`: Permite conectarse a un cliente en espera para iniciar el chat de soporte.
*   **Gestión de Inventario**:
    *   `:stockin [carta] [precio]`: Ingresar una nueva carta a la bodega interna.
    *   `:publish [carta] [precio]`: Mover una carta de la bodega al catálogo público.
    *   `:reprice [carta] [precio]`: Actualizar el precio de un ítem publicado.
    *   `:moveout [carta]`: Retirar una carta del catálogo hacia bodega.
*   **Gestión de Finanzas y Envíos**:
    *   `:orders` y `:ship [order_id]`: Revisar lista de órdenes y confirmar su envío.
    *   `:deposits` y `:approve [deposit_id]`: Revisar y aprobar solicitudes de saldo de los clientes.
    *   `:returns` y `:accept [order_id]`: Gestionar las devoluciones solicitadas.
*   `:exit`: Cerrar la sesión del ejecutivo de forma segura.