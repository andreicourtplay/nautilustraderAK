# Seguimiento del proyecto NautilusTrader + IBKR Paper

Fecha de actualizacion: 2026-06-30

Este documento es el checklist local de seguimiento del proyecto. La idea es usarlo como panel simple: que esta hecho, que falta, que se debe probar y cual es el siguiente bloque de trabajo.

## Estado rapido

- [x] Proyecto local creado en `/Users/andrei/Desktop/NAUTILUS TRADER`.
- [x] NautilusTrader instalado con soporte Interactive Brokers.
- [x] Flujo sin Docker decidido y aplicado.
- [x] TWS paper configurado con API socket.
- [x] Conexion con IBKR paper validada.
- [x] Primera orden paper real ejecutada: `BUY 1 AAPL MKT`.
- [x] Repositorio Git inicializado.
- [x] Remoto GitHub configurado: `https://github.com/andreicourtplay/nautilustraderAK.git`.
- [x] Ramas creadas y subidas: `main`, `dev/andrei`, `dev/fran`.
- [x] Rama activa de trabajo para Andrei: `dev/andrei`.
- [x] Primer flujo de estrategia minima creado y probado en modo seguro.
- [ ] Backtest minimo preparado.
- [ ] Sistema de resultados/backtests creado.
- [ ] Estrategia real de prueba definida.
- [ ] Revision con Fran del flujo de trabajo desde su ordenador.

## Hecho hasta ahora

### Base tecnica

- [x] Crear entorno Python local con `.venv`.
- [x] Instalar dependencias con `uv`.
- [x] Instalar `nautilus-trader[ib]`.
- [x] Crear `pyproject.toml`.
- [x] Crear `uv.lock`.
- [x] Crear `.gitignore`.
- [x] Ignorar `.env`, `.venv`, `.uv-cache`, logs reales, `tmp` y capturas.
- [x] Crear estructura base:
  - [x] `scripts/`
  - [x] `strategies/`
  - [x] `config/`
  - [x] `logs/`
  - [x] `data/`
  - [x] `docs/`
  - [x] `tools/`

### Configuracion IBKR / TWS

- [x] Abrir Trader Workstation en cuenta paper.
- [x] Confirmar cuenta paper `DU...`.
- [x] Activar `Enable ActiveX and Socket Clients`.
- [x] Usar puerto TWS paper `7497`.
- [x] Desactivar `Read-Only API` para permitir ordenes paper.
- [x] Validar conexion por socket local.
- [x] Validar conexion desde NautilusTrader.
- [x] Confirmar cuenta devuelta por IBKR.
- [x] Confirmar posiciones y ordenes abiertas desde script.

### Operativa paper basica

- [x] Crear script `scripts/ib_connection_check.py`.
- [x] Crear script `scripts/ib_paper_order.py`.
- [x] Enviar prueba `whatIf`.
- [x] Ejecutar orden paper real de prueba: `BUY 1 AAPL MKT`.
- [x] Confirmar posicion AAPL en TWS/IBKR.
- [x] Crear script `scripts/ib_status.py`.
- [x] Confirmar estado actual:
  - [x] 1 posicion AAPL.
  - [x] 0 ordenes abiertas.
  - [x] 1 ejecucion registrada del dia de la prueba.

### Seguridad paper-only

- [x] Crear `scripts/ib_safety.py`.
- [x] Bloquear cuentas que no parezcan paper salvo override explicito.
- [x] Exigir confirmacion para transmitir ordenes paper.
- [x] Limitar cantidad maxima con `IB_MAX_ORDER_QUANTITY`.
- [x] Limitar simbolos permitidos con `IB_ALLOWED_SYMBOLS`.
- [x] Mantener `whatIf` como comportamiento seguro por defecto.

### Logs y trazabilidad

- [x] Crear `scripts/ib_logging.py`.
- [x] Crear log de conexiones: `logs/connection_checks.log`.
- [x] Crear log de ordenes: `logs/orders.csv`.
- [x] Crear log de ejecuciones/resumen: `logs/executions.csv`.
- [x] Crear log de decisiones de estrategia: `logs/strategy_decisions.csv`.
- [x] Confirmar que los logs reales no se suben a Git.

### Colaboracion Andrei / Fran

- [x] Crear documentacion de colaboracion: `docs/COLLABORATION.md`.
- [x] Definir ramas:
  - [x] `main`: rama estable.
  - [x] `dev/andrei`: rama de Andrei.
  - [x] `dev/fran`: rama de Fran.
- [x] Subir ramas a GitHub.
- [x] Definir que cada persona tiene su propio `.env`.
- [x] Definir que no se comparten credenciales ni logs privados.
- [x] Definir `IB_CLIENT_ID` separado si se conectan al mismo TWS.

### Documentacion creada

- [x] `README.md`.
- [x] `docs/COLLABORATION.md`.
- [x] `docs/STRATEGY_WORKFLOW.md`.
- [x] `docs/manual_basico_tws.docx`.
- [x] `docs/plan_global_nautilus_ibkr.docx`.
- [x] `docs/SEGUIMIENTO_PROYECTO.md`.

### Primera estrategia minima

- [x] Crear `strategies/single_symbol_entry.py`.
- [x] Crear `scripts/run_minimal_strategy.py`.
- [x] Crear `scripts/ib_orders.py`.
- [x] Separar logica pura de estrategia y conexion con IBKR.
- [x] Decidir `SKIP` si ya existe posicion.
- [x] Decidir `SKIP` si hay ordenes abiertas.
- [x] Decidir `ORDER` si no hay posicion ni ordenes abiertas.
- [x] Probar con `AAPL`: resultado esperado `SKIP`.
- [x] Probar con `IBKR`: resultado esperado `ORDER` en modo `whatIf`.
- [x] Confirmar que `IBKR whatIf` no deja orden abierta ni posicion nueva.

## Pendiente por bloques

### Bloque 1 - Limpieza y control de proyecto

- [x] Inicializar Git.
- [x] Subir ramas a GitHub.
- [x] Dejar `.env` fuera del repo.
- [x] Documentar instalacion basica.
- [ ] Revisar si queremos proteger `main` en GitHub con Pull Requests.
- [ ] Crear reglas de trabajo para merges entre Andrei y Fran.
- [ ] Decidir si cada cambio pasa primero por PR o si se hara merge manual.

### Bloque 2 - Backtest minimo

- [ ] Definir fuente de datos historicos.
- [ ] Decidir si el primer backtest usa datos descargados o datos mock.
- [ ] Crear carpeta de resultados de backtest.
- [ ] Crear script de backtest minimo.
- [ ] Guardar resultado en CSV/JSON.
- [ ] Medir al menos:
  - [ ] numero de trades.
  - [ ] P&L aproximado.
  - [ ] win rate.
  - [ ] drawdown simple.
  - [ ] posicion final.
- [ ] Documentar como ejecutar el backtest.
- [ ] Subir backtest base a `main`, `dev/andrei` y `dev/fran` cuando este verificado.

### Bloque 3 - Datos de mercado

- [ ] Confirmar que datos de mercado estan activos en paper para simbolos elegidos.
- [ ] Crear script para ultimo precio / bid / ask.
- [ ] Crear script para barras historicas si IBKR lo permite.
- [ ] Guardar muestras de datos en `data/` solo si no contienen informacion sensible.
- [ ] Documentar limitaciones de datos paper.

### Bloque 4 - Estrategia real de prueba

- [ ] Definir una idea de estrategia simple.
- [ ] Definir instrumentos permitidos.
- [ ] Definir horario de ejecucion.
- [ ] Definir maximo de operaciones por dia.
- [ ] Definir cierre de posicion.
- [ ] Definir cuando no operar.
- [ ] Implementar version 1.
- [ ] Probar primero con backtest.
- [ ] Probar despues con `whatIf`.
- [ ] Probar por ultimo en paper con tamano minimo.

### Bloque 5 - Gestion de riesgo

- [x] Bloquear no-paper por defecto.
- [x] Limitar cantidad maxima por orden.
- [x] Limitar simbolos permitidos.
- [ ] Limite maximo de ordenes por dia.
- [ ] Limite maximo de posicion por simbolo.
- [ ] Bloqueo si hay orden abierta del mismo simbolo.
- [ ] Bloqueo si TWS devuelve errores.
- [ ] Bloqueo si no hay datos de mercado.
- [ ] Cierre/alerta si queda posicion abierta al final de una prueba.

### Bloque 6 - Trabajo de Fran

- [ ] Fran clona el repo.
- [ ] Fran cambia a `dev/fran`.
- [ ] Fran ejecuta `uv sync`.
- [ ] Fran crea su `.env`.
- [ ] Fran abre su TWS paper.
- [ ] Fran valida `scripts/check_install.py`.
- [ ] Fran valida `scripts/ib_connection_check.py`.
- [ ] Fran ejecuta `scripts/ib_status.py`.
- [ ] Fran prueba estrategia minima en `whatIf`.
- [ ] Fran confirma que no sube `.env` ni logs.

### Bloque 7 - Paper trading controlado

- [x] Primera orden paper manual hecha.
- [x] Primera estrategia minima probada en `whatIf`.
- [ ] Definir checklist antes de cada prueba paper.
- [ ] Definir checklist despues de cada prueba paper.
- [ ] Ejecutar prueba paper con estrategia solo cuando el backtest minimo exista.
- [ ] Revisar logs tras cada ejecucion.
- [ ] Revisar TWS tras cada ejecucion.
- [ ] Documentar resultado de cada sesion.

## Comandos utiles

### Ver rama actual

```bash
git status --short --branch
```

### Cambiar a rama de Andrei

```bash
git checkout dev/andrei
```

### Cambiar a rama de Fran

```bash
git checkout dev/fran
```

### Verificar instalacion

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/check_install.py
```

### Comprobar conexion IBKR

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_connection_check.py
```

### Ver estado de cuenta paper

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/ib_status.py
```

### Lanzar estrategia minima en modo seguro

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_minimal_strategy.py
```

### Probar `whatIf` con IBKR

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_minimal_strategy.py --symbol IBKR
```

### Transmitir orden paper solo con confirmacion

```bash
UV_CACHE_DIR=.uv-cache /opt/homebrew/bin/uv run python scripts/run_minimal_strategy.py --symbol IBKR --submit-paper-order --confirm-paper-trade
```

## Reglas que no debemos romper

- [ ] No operar cuenta real.
- [ ] No subir `.env`.
- [ ] No subir credenciales.
- [ ] No subir logs reales.
- [ ] No subir capturas con cuenta visible.
- [ ] No aumentar cantidad sin revisar `IB_MAX_ORDER_QUANTITY`.
- [ ] No permitir simbolos nuevos sin anadirlos a `IB_ALLOWED_SYMBOLS`.
- [ ] No ejecutar estrategia en paper real sin revisar primero `whatIf`.
- [ ] No mezclar trabajo de Andrei y Fran en la misma rama.

## Proximo paso recomendado

El siguiente paso tecnico recomendado es el backtest minimo:

- [ ] Crear script de backtest simple.
- [ ] Usar datos mock o historicos controlados.
- [ ] Guardar resultados en `data/backtests/` o `logs/backtests/`.
- [ ] Documentar el resultado.
- [ ] No avanzar a mas paper trading automatico hasta que este bloque exista.

## Historial de hitos

- [x] 2026-06-29: instalacion y configuracion inicial NautilusTrader + IBKR paper.
- [x] 2026-06-29: TWS API activada y conexion validada.
- [x] 2026-06-29: primera orden paper `BUY 1 AAPL MKT` ejecutada.
- [x] 2026-06-29: manual basico de TWS creado.
- [x] 2026-06-29: plan global del proyecto creado.
- [x] 2026-06-29: GitHub remoto y ramas `main`, `dev/andrei`, `dev/fran` creadas.
- [x] 2026-06-29: seguridad paper-only, logs y comando de estado creados.
- [x] 2026-06-29: estrategia minima creada y probada en `whatIf`.
- [x] 2026-06-30: checklist local de seguimiento creado.
