# Manual de Cileo (cileo.io/manual)

Esta carpeta genera la página pública del manual, que además es la **fuente de
conocimiento del bot de Respond.io**: Respond la lee como fuente de tipo *Website*
y vuelve a sincronizarla sola. Por eso el texto tiene que vivir en el HTML servido
y no depender de JavaScript.

## Cómo se actualiza (rutina semanal)

1. Edita **`fuente-manual.txt`**. Es el único archivo que se toca a mano.
2. Regenera la página:

   ```
   python manual/construir_manual.py
   ```

3. Revisa que diga `Verificacion OK` y haz commit de `fuente-manual.txt`
   y de `index.html` juntos.

Para validar sin escribir el HTML: `python manual/construir_manual.py --verificar`

## Qué verifica el generador

- Que no haya saltos de encabezado (h1 → h2 → h3) ni anclas duplicadas.
- Que todo enlace interno tenga su destino.
- Que la página quede envuelta entre `<!--email_off-->` y `<!--/email_off-->`
  (sin eso, Cloudflare ofusca `soporte@cileo.io` y el rastreador del bot no lo lee).
- Que las etiquetas estén balanceadas.
- Que **cada texto de la fuente aparezca en el HTML**, para que no se pierda nada.

## Estructura

| Archivo | Qué es |
|---|---|
| `fuente-manual.txt` | El contenido. Lo que se edita. |
| `construir_manual.py` | El generador. Las directivas están documentadas en su encabezado. |
| `index.html` | Generado. **No editar a mano.** |
| `parciales/` | Fragmentos reutilizados (logotipo y lupa del menú). |
| `../assets/img/manual/` | Las capturas, en WebP. |

## Reglas de contenido

- Solo de cara al usuario: nada de arquitectura interna, bugs ni nombres de clientes.
- Español de México.
- Lo que es **comportamiento del bot** (cuándo transferir a una persona, qué no
  suponer, qué no cubre la guía) **no va aquí**: eso vive en las instrucciones de
  los agentes en Respond.io.

## Capturas

Están en `../assets/img/manual/` en WebP. Para reemplazar una, conserva el nombre
del archivo y la referencia en `fuente-manual.txt` no cambia. Las marcas numeradas
sobre cada captura se definen con `MARCAS:` usando porcentajes de posición.
