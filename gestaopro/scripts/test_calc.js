/**
 * GestãoPro — Testes da Calculadora (EX8)
 * 40 testes Node.js puros — sem framework externo (usa assert nativo).
 *
 * Executar: node scripts/test_calc.js
 *
 * Cobertura:
 *  - Operações básicas (+, −, ×, ÷)
 *  - Precedência matemática (× e ÷ antes de + e −)
 *  - Precisão de ponto flutuante (0.1+0.2=0.3)
 *  - Números negativos
 *  - Decimais
 *  - Porcentagem
 *  - Inversão de sinal
 *  - Backspace
 *  - Clear
 *  - Divisão por zero
 *  - Histórico
 *  - Entrada de múltiplos dígitos
 *  - Expressões complexas
 */
'use strict';

const assert = require('assert');
const CalcEngine = require('../frontend/js/calc-engine.js');

const { evaluate, formatNumber, round10, isOp, createCalc } = CalcEngine;

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (e) {
    console.error(`  ✗ ${name}`);
    console.error(`    → ${e.message}`);
    failed++;
  }
}

// ═════════════════════════════════════════════════════════════════
// 1. Operações básicas
// ═════════════════════════════════════════════════════════════════
console.log('\n── Operações básicas ──');

test('adição simples: 2 + 3 = 5', () => {
  assert.strictEqual(evaluate(['2', '+', '3']), 5);
});

test('subtração: 10 − 4 = 6', () => {
  assert.strictEqual(evaluate(['10', '−', '4']), 6);
});

test('multiplicação: 3 × 4 = 12', () => {
  assert.strictEqual(evaluate(['3', '×', '4']), 12);
});

test('divisão: 15 ÷ 3 = 5', () => {
  assert.strictEqual(evaluate(['15', '÷', '3']), 5);
});

test('número único retorna si mesmo: 42', () => {
  assert.strictEqual(evaluate(['42']), 42);
});

// ═════════════════════════════════════════════════════════════════
// 2. Precisão de ponto flutuante
// ═════════════════════════════════════════════════════════════════
console.log('\n── Precisão de ponto flutuante ──');

test('0.1 + 0.2 = 0.3 (sem erro de float)', () => {
  assert.strictEqual(evaluate(['0.1', '+', '0.2']), 0.3);
});

test('0.1 + 0.2 não é 0.30000000000000004', () => {
  assert.notStrictEqual(0.1 + 0.2, 0.3);          // JS nativo falha
  assert.strictEqual(evaluate(['0.1', '+', '0.2']), 0.3); // motor corrige
});

test('1.1 + 2.2 = 3.3', () => {
  assert.strictEqual(evaluate(['1.1', '+', '2.2']), 3.3);
});

test('0.3 − 0.1 = 0.2', () => {
  assert.strictEqual(evaluate(['0.3', '−', '0.1']), 0.2);
});

// ═════════════════════════════════════════════════════════════════
// 3. Precedência matemática
// ═════════════════════════════════════════════════════════════════
console.log('\n── Precedência matemática ──');

test('2 + 3 × 4 = 14 (não 20)', () => {
  assert.strictEqual(evaluate(['2', '+', '3', '×', '4']), 14);
});

test('10 − 2 × 3 = 4 (não 24)', () => {
  assert.strictEqual(evaluate(['10', '−', '2', '×', '3']), 4);
});

test('6 ÷ 2 + 3 = 6 (não 1)', () => {
  assert.strictEqual(evaluate(['6', '÷', '2', '+', '3']), 6);
});

test('1 + 2 × 3 − 4 ÷ 2 = 5', () => {
  assert.strictEqual(evaluate(['1', '+', '2', '×', '3', '−', '4', '÷', '2']), 5);
});

test('4 × 3 + 2 × 5 = 22', () => {
  assert.strictEqual(evaluate(['4', '×', '3', '+', '2', '×', '5']), 22);
});

// ═════════════════════════════════════════════════════════════════
// 4. Números negativos
// ═════════════════════════════════════════════════════════════════
console.log('\n── Números negativos ──');

test('−5 + 3 = −2', () => {
  assert.strictEqual(evaluate(['-5', '+', '3']), -2);
});

test('−3 × −4 = 12', () => {
  assert.strictEqual(evaluate(['-3', '×', '-4']), 12);
});

test('0 − 7 = −7', () => {
  assert.strictEqual(evaluate(['0', '−', '7']), -7);
});

// ═════════════════════════════════════════════════════════════════
// 5. Divisão por zero
// ═════════════════════════════════════════════════════════════════
console.log('\n── Divisão por zero ──');

test('divisão por zero lança DIVISION_BY_ZERO', () => {
  assert.throws(() => evaluate(['5', '÷', '0']), /DIVISION_BY_ZERO/);
});

test('divisão por zero no estado retorna status error', () => {
  const c = createCalc();
  c.inputDigit('5');
  c.inputOp('÷');
  c.inputDigit('0');
  const r = c.inputAction('equals');
  assert.strictEqual(r.status, 'error');
  assert.strictEqual(r.error, 'DIVISION_BY_ZERO');
});

// ═════════════════════════════════════════════════════════════════
// 6. formatNumber
// ═════════════════════════════════════════════════════════════════
console.log('\n── formatNumber ──');

test('formatNumber(3.0) = "3"', () => {
  assert.strictEqual(formatNumber(3.0), '3');
});

test('formatNumber(3.5) = "3.5"', () => {
  assert.strictEqual(formatNumber(3.5), '3.5');
});

test('formatNumber(3.50) = "3.5"', () => {
  assert.strictEqual(formatNumber(3.50), '3.5');
});

test('formatNumber(0) = "0"', () => {
  assert.strictEqual(formatNumber(0), '0');
});

// ═════════════════════════════════════════════════════════════════
// 7. Estado da calculadora — createCalc()
// ═════════════════════════════════════════════════════════════════
console.log('\n── Estado da calculadora ──');

test('digit input acumula display', () => {
  const c = createCalc();
  c.inputDigit('1');
  c.inputDigit('2');
  c.inputDigit('3');
  assert.strictEqual(c.getState().display, '123');
});

test('ponto decimal único por número', () => {
  const c = createCalc();
  c.inputDigit('3');
  c.inputDigit('.');
  c.inputDigit('1');
  c.inputDigit('.');  // segundo ponto ignorado
  c.inputDigit('4');
  assert.strictEqual(c.getState().display, '3.14');
});

test('clear reseta tudo', () => {
  const c = createCalc();
  c.inputDigit('9');
  c.inputOp('+');
  c.inputDigit('5');
  c.inputAction('clear');
  const s = c.getState();
  assert.strictEqual(s.display, '0');
  assert.strictEqual(s.tokens.length, 0);
});

test('backspace remove último caractere', () => {
  const c = createCalc();
  c.inputDigit('1');
  c.inputDigit('2');
  c.inputDigit('3');
  c.inputAction('backspace');
  assert.strictEqual(c.getState().display, '12');
});

test('backspace em single-char retorna "0"', () => {
  const c = createCalc();
  c.inputDigit('7');
  c.inputAction('backspace');
  assert.strictEqual(c.getState().display, '0');
});

test('inversão de sinal positivo → negativo', () => {
  const c = createCalc();
  c.inputDigit('5');
  c.inputAction('sign');
  assert.strictEqual(c.getState().display, '-5');
});

test('inversão de sinal negativo → positivo', () => {
  const c = createCalc();
  c.inputDigit('5');
  c.inputAction('sign');
  c.inputAction('sign');
  assert.strictEqual(c.getState().display, '5');
});

test('porcentagem: 50 → 0.5', () => {
  const c = createCalc();
  c.inputDigit('5');
  c.inputDigit('0');
  c.inputAction('pct');
  assert.strictEqual(c.getState().display, '0.5');
});

test('cálculo 2 + 3 × 4 = 14 pelo estado', () => {
  const c = createCalc();
  c.inputDigit('2');
  c.inputOp('+');
  c.inputDigit('3');
  c.inputOp('×');
  c.inputDigit('4');
  const r = c.inputAction('equals');
  assert.strictEqual(r.status, 'ok');
  assert.strictEqual(r.display, '14');
});

// ═════════════════════════════════════════════════════════════════
// 8. Histórico
// ═════════════════════════════════════════════════════════════════
console.log('\n── Histórico ──');

test('histórico registra cálculo', () => {
  const c = createCalc();
  c.inputDigit('5');
  c.inputOp('+');
  c.inputDigit('3');
  c.inputAction('equals');
  assert.strictEqual(c.getHistory().length, 1);
  assert.strictEqual(c.getHistory()[0].result, '8');
});

test('histórico mantém múltiplos cálculos em ordem (mais recente primeiro)', () => {
  const c = createCalc();
  // Cálculo 1: 1 + 1
  c.inputDigit('1'); c.inputOp('+'); c.inputDigit('1'); c.inputAction('equals');
  // Cálculo 2: 9 + 1
  c.inputDigit('9'); c.inputOp('+'); c.inputDigit('1'); c.inputAction('equals');
  const h = c.getHistory();
  assert.strictEqual(h.length, 2);
  assert.strictEqual(h[0].result, '10'); // mais recente primeiro
  assert.strictEqual(h[1].result, '2');
});

test('clearHistory esvazia o histórico', () => {
  const c = createCalc();
  c.inputDigit('3'); c.inputOp('+'); c.inputDigit('3'); c.inputAction('equals');
  c.clearHistory();
  assert.strictEqual(c.getHistory().length, 0);
});

// ═════════════════════════════════════════════════════════════════
// 9. Erros
// ═════════════════════════════════════════════════════════════════
console.log('\n── Erros ──');

test('tokens vazios lança INVALID_EXPRESSION', () => {
  assert.throws(() => evaluate([]), /INVALID_EXPRESSION/);
});

test('token inválido lança INVALID_TOKEN', () => {
  assert.throws(() => evaluate(['abc']), /INVALID_TOKEN/);
});

test('expressão incompleta (só operador) lança erro', () => {
  assert.throws(() => evaluate(['+']), (e) => {
    return e.message === 'INVALID_TOKEN' || e.message === 'INVALID_EXPRESSION';
  });
});

// ═════════════════════════════════════════════════════════════════
// Resultado final
// ═════════════════════════════════════════════════════════════════
console.log(`\n${'═'.repeat(50)}`);
console.log(`Resultado: ${passed} aprovados, ${failed} reprovados de ${passed + failed} testes`);
if (failed > 0) {
  console.error(`\n❌ ${failed} teste(s) falharam!`);
  process.exit(1);
} else {
  console.log(`\n✅ Todos os ${passed} testes passaram!`);
}
