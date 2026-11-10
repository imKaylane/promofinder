/**
 * GestãoPro — Motor da Calculadora (EX8)
 * Implementação sem eval().
 * Algoritmo: Shunting-Yard + Avaliação RPN.
 *
 * Requisitos atendidos:
 * - Adição, subtração, multiplicação, divisão
 * - Números negativos e decimais
 * - Porcentagem (÷100)
 * - Inversão de sinal (±)
 * - Backspace e Clear
 * - Histórico (últimos 50 cálculos)
 * - Precedência matemática (× e ÷ antes de + e −)
 * - Divisão por zero → "Erro: divisão por zero"
 * - Precisão de ponto flutuante:
 *     0,1 + 0,2 = 0,3  ✓
 *     2 + 3 × 4 = 14   ✓
 *
 * Exporta como módulo CommonJS (compatível com Node.js para testes)
 * e também registra window.CalcEngine para uso em browsers.
 */

(function (exports) {
  'use strict';

  const _OP_SYMBOLS = ['+', '−', '×', '÷'];
  const _PRECEDENCE  = { '+': 1, '−': 1, '×': 2, '÷': 2 };

  // ── Arredondamento para evitar erro de ponto flutuante ──────────────────────
  // Ex: 0.1 + 0.2 → Math.round(0.30000000000000004 × 1e10) / 1e10 = 0.3
  function round10(n) {
    return Math.round(n * 1e10) / 1e10;
  }

  // ── Parsing ─────────────────────────────────────────────────────────────────
  function parseNum(s) {
    const n = parseFloat(String(s));
    if (isNaN(n)) throw new Error('INVALID_TOKEN');
    return n;
  }

  function isOp(t) {
    return _OP_SYMBOLS.includes(t);
  }

  // ── Shunting-Yard: tokens → RPN (Reverse Polish Notation) ──────────────────
  function toRPN(tokens) {
    const output = [];
    const ops    = [];
    for (const tok of tokens) {
      if (isOp(tok)) {
        while (ops.length > 0 && _PRECEDENCE[ops[ops.length - 1]] >= _PRECEDENCE[tok]) {
          output.push(ops.pop());
        }
        ops.push(tok);
      } else {
        output.push(parseNum(tok));
      }
    }
    while (ops.length > 0) output.push(ops.pop());
    return output;
  }

  // ── Avaliação RPN ────────────────────────────────────────────────────────────
  function evalRPN(rpn) {
    const stack = [];
    for (const tok of rpn) {
      if (typeof tok === 'number') {
        stack.push(tok);
      } else {
        const b = stack.pop();
        const a = stack.pop();
        if (a === undefined || b === undefined) throw new Error('INVALID_EXPRESSION');
        switch (tok) {
          case '+': stack.push(round10(a + b)); break;
          case '−': stack.push(round10(a - b)); break;
          case '×': stack.push(round10(a * b)); break;
          case '÷':
            if (b === 0) throw new Error('DIVISION_BY_ZERO');
            stack.push(round10(a / b));
            break;
          default:
            throw new Error('UNKNOWN_OPERATOR');
        }
      }
    }
    if (stack.length !== 1) throw new Error('INVALID_EXPRESSION');
    return stack[0];
  }

  // ── Avaliação pública ─────────────────────────────────────────────────────
  /**
   * Avalia uma expressão representada como array de tokens.
   * Tokens são strings: números ("3.14", "-5") ou operadores ("+", "−", "×", "÷").
   *
   * @param {string[]} tokens
   * @returns {number}
   * @throws {Error} DIVISION_BY_ZERO | INVALID_EXPRESSION | INVALID_TOKEN
   */
  function evaluate(tokens) {
    if (!Array.isArray(tokens) || tokens.length === 0) {
      throw new Error('INVALID_EXPRESSION');
    }
    const rpn = toRPN(tokens);
    return evalRPN(rpn);
  }

  // ── Formatação de número ──────────────────────────────────────────────────
  /**
   * Remove zeros finais desnecessários após o ponto decimal.
   * Ex: "3.0" → "3", "3.50" → "3.5"
   */
  function formatNumber(n) {
    if (!isFinite(n)) return String(n);
    const s = n.toString();
    if (s.includes('.')) return s.replace(/\.?0+$/, '') || '0';
    return s;
  }

  // ── Estado da calculadora ─────────────────────────────────────────────────
  /**
   * Cria uma instância do estado da calculadora.
   * Útil para testes e para embbed no frontend.
   */
  function createCalc() {
    let display    = '0';
    let tokens     = [];       // ["3", "+", "5", "×", …]
    let expression = '';
    let justCalc   = false;
    let history    = [];

    function getState() {
      return { display, tokens: tokens.slice(), expression, justCalc };
    }

    function inputDigit(d) {
      if (d === undefined || d === null) return;
      const digit = String(d);
      if (justCalc && digit !== '.') {
        display = ''; tokens = []; expression = '';
      }
      justCalc = false;

      if (digit === '.') {
        if (display.includes('.')) return;
        if (display === '' || display === '-') display += '0';
        display += '.';
        return;
      }
      if (display === '0') display = digit;
      else display += digit;
    }

    function inputOp(op) {
      if (!isOp(op)) throw new Error('UNKNOWN_OPERATOR');
      justCalc = false;
      if (display !== '') {
        tokens.push(display);
        display = '';
      }
      // Replace last operator if two in a row
      if (tokens.length > 0 && isOp(tokens[tokens.length - 1])) {
        tokens[tokens.length - 1] = op;
      } else {
        tokens.push(op);
      }
      expression = tokens.join(' ') + ' ';
    }

    function inputAction(action) {
      switch (action) {
        case 'clear':
          display = '0'; tokens = []; expression = ''; justCalc = false;
          return { status: 'ok' };

        case 'backspace':
          if (justCalc) { display = '0'; justCalc = false; break; }
          display = display.length > 1 ? display.slice(0, -1) : '0';
          break;

        case 'sign':
          if (display === '0' || display === '') return { status: 'ok' };
          display = display.startsWith('-') ? display.slice(1) : '-' + display;
          break;

        case 'pct': {
          const v = parseNum(display || '0');
          display = formatNumber(round10(v / 100));
          break;
        }

        case 'equals':
          return _calculate();

        default:
          throw new Error('UNKNOWN_ACTION');
      }
      return { status: 'ok', display };
    }

    function _calculate() {
      const allTokens = display !== '' ? tokens.concat(display) : tokens.slice();
      if (allTokens.length === 0) return { status: 'ok', display };

      const expr = allTokens.join(' ');
      try {
        const result = evaluate(allTokens);
        const resultStr = formatNumber(result);
        history.unshift({ expression: expr + ' =', result: resultStr, ts: new Date().toISOString() });
        if (history.length > 50) history.pop();

        display = resultStr;
        tokens  = [];
        expression = expr + ' =';
        justCalc = true;

        return { status: 'ok', display: resultStr, expression: expr + ' =' };
      } catch (e) {
        const msg = e.message === 'DIVISION_BY_ZERO' ? 'Erro: divisão por zero' : 'Erro de cálculo';
        tokens  = [];
        display = '0';
        justCalc = true;
        return { status: 'error', error: e.message, display: msg };
      }
    }

    function getHistory() { return history.slice(); }
    function clearHistory() { history = []; }

    return { inputDigit, inputOp, inputAction, getState, getHistory, clearHistory };
  }

  // ── Exports ──────────────────────────────────────────────────────────────────
  const CalcEngine = { evaluate, formatNumber, round10, isOp, createCalc };

  // Browser global
  if (typeof window !== 'undefined') {
    window.CalcEngine = CalcEngine;
  }

  // CommonJS (Node.js / testes)
  if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = CalcEngine;
  }

}({}));
