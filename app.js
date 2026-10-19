// ChemScan AR - app logic
//
// 1. Load the lot records from products.json.
// 2. Color each label's AR badge by its QC status.
// 3. When MindAR recognizes a label (targetFound), show that lot in the bottom panel.
// 4. Keep the panel up until "Scan Next" is tapped or a different label is recognized.

let products = [];        // the records from products.json
let currentIndex = null;  // target index whose details are on screen (null = panel empty)

// How each QC status looks, in the panel and on the AR badge
const STATUS_STYLES = {
  'Released': { cssClass: 'status-released', icon: '✓', color: '#137a36', textColor: '#ffffff' },
  'On Hold':  { cssClass: 'status-on-hold',  icon: '!', color: '#ffc107', textColor: '#000000' },
  'Expired':  { cssClass: 'status-expired',  icon: '✕', color: '#c62828', textColor: '#ffffff' }
};

// Shortcut for document.getElementById
const $ = (id) => document.getElementById(id);

async function loadProducts() {
  const response = await fetch('./products.json');
  if (!response.ok) {
    throw new Error('Could not load products.json (HTTP ' + response.status + ')');
  }
  products = await response.json();
}

// Find the record for a MindAR target index (0, 1, 2)
function findProduct(targetIndex) {
  return products.find((p) => p.targetIndex === targetIndex) || null;
}

// Fill the bottom panel with one product's details
function showProduct(targetIndex) {
  if (targetIndex === currentIndex) return;  // same label seen again: panel is already right

  const product = findProduct(targetIndex);
  if (!product) {
    console.warn('No product record for target index', targetIndex);
    return;
  }
  currentIndex = targetIndex;

  const style = STATUS_STYLES[product.qcStatus];
  const status = $('qc-status');
  status.className = 'qc-status ' + style.cssClass;
  status.textContent = style.icon + ' ' + product.qcStatus.toUpperCase();

  $('product-name').textContent = product.productName;
  $('date-label').textContent = product.dateType;    // "Retest" or "Expiration"
  $('date-value').textContent = product.date;
  $('lot-value').textContent = product.lotNumber;
  $('storage-value').textContent = product.storage;

  $('details-panel').hidden = false;
  $('scan-hint').hidden = true;
}

// Empty the panel and go back to "point the camera" mode
function clearPanel() {
  currentIndex = null;
  $('details-panel').hidden = true;
  $('scan-hint').hidden = false;
}

// Set up each label's AR badge and listen for MindAR finding it
function setupTargets() {
  // The .label-target entities are in index.html in target order, so their position = target index
  document.querySelectorAll('.label-target').forEach((target, index) => {
    const product = findProduct(index);
    if (!product) return;
    const style = STATUS_STYLES[product.qcStatus];

    target.querySelector('.tint').setAttribute('color', style.color);
    target.querySelector('.badge').setAttribute('color', style.color);
    const text = target.querySelector('.badge-text');
    text.setAttribute('value', product.qcStatus.toUpperCase());
    text.setAttribute('color', style.textColor);

    // MindAR fires targetFound when this label appears in the camera.
    // We ignore targetLost on purpose so the panel stays readable.
    target.addEventListener('targetFound', () => showProduct(index));
  });
}

async function init() {
  try {
    await loadProducts();
  } catch (err) {
    console.error(err);
    $('scan-hint').textContent = 'Error: could not load product data.';
    return;
  }
  setupTargets();
  $('scan-next').addEventListener('click', clearPanel);
}

init();
