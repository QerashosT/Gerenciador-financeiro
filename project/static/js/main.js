// 1. LÓGICA DA MÁSCARA
function initializeMasks() {
    const currencyWrappers = document.querySelectorAll('.currency-input-wrapper');

    currencyWrappers.forEach(wrapper => {
        const visibleMaskInput = wrapper.querySelector('.currency-mask');
        const hiddenValueInput = wrapper.querySelector('.hidden-currency-value');

        // Impede que a máscara seja inicializada duas vezes no mesmo elemento
        if (visibleMaskInput.imask) { return; }

        // Usando a sua configuração de máscara original
        const maskOptions = {
            mask: 'num',
            blocks: {
                num: {
                    mask: Number,
                    scale: 2, // 2 casas decimais
                    thousandsSeparator: '.', // Separador de milhar
                    padFractionalZeros: true, // Adiciona ",00"
                    normalizeZeros: true,
                    radix: ',', // Separador decimal
                    mapToRadix: ['.'], // Mapeia "." para ","
                    min: 0
                }
            }
        };

        const mask = IMask(visibleMaskInput, maskOptions);

        // Quando carrega (ex: editar ou erro de validação)
        if (hiddenValueInput.value) {
            mask.value = hiddenValueInput.value;
        }

        // Quando o usuário digita
        mask.on('accept', () => {
            // Salva o valor numérico (ex: "1234.56") no campo escondido
            hiddenValueInput.value = mask.unmaskedValue;
        });
    });
}

// 2. LÓGICA DO MODAL
const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
const modalCloses = document.querySelectorAll('[data-modal-close]');

modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
        const modalId = trigger.dataset.modalTrigger;
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('is-open');
            // REMOVIDO: initializeMasks() - Não precisa reinicializar!
        }
    });
});

modalCloses.forEach(close => {
    close.addEventListener('click', () => {
        const modalId = close.dataset.modalClose;
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('is-open');
        }
    });
});

// 3. Inicializa as máscaras UMA ÚNICA VEZ na carga da página
// Isso inclui os campos dentro dos modais (mesmo que estejam ocultos)
initializeMasks();