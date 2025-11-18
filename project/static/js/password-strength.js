document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[name="password"]');

    if (!passwordInput) return;

    // Criar indicador de força
    const strengthIndicator = document.createElement('div');
    strengthIndicator.className = 'password-strength';
    strengthIndicator.innerHTML = `
        <div class="strength-bar">
            <div class="strength-bar-fill"></div>
        </div>
        <p class="strength-text">Digite uma senha</p>
    `;

    // Inserir após o input de senha
    passwordInput.parentElement.appendChild(strengthIndicator);

    // Função para calcular força da senha
    function checkPasswordStrength(password) {
        let strength = 0;
        const feedback = [];

        // Critérios
        if (password.length >= 8) {
            strength += 20;
        } else {
            feedback.push('Mínimo 8 caracteres');
        }

        if (password.length >= 12) strength += 10;

        if (/[a-z]/.test(password)) {
            strength += 20;
        } else {
            feedback.push('Adicione letras minúsculas');
        }

        if (/[A-Z]/.test(password)) {
            strength += 20;
        } else {
            feedback.push('Adicione letras MAIÚSCULAS');
        }

        if (/\d/.test(password)) {
            strength += 20;
        } else {
            feedback.push('Adicione números');
        }

        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            strength += 20;
        } else {
            feedback.push('Adicione caracteres especiais (!@#$%)');
        }

        // Senhas comuns
        const commonPasswords = ['password', '123456', 'qwerty', 'senha'];
        if (commonPasswords.some(common => password.toLowerCase().includes(common))) {
            strength = Math.min(strength, 40);
            feedback.unshift('⚠️ Senha muito comum');
        }

        return { strength, feedback };
    }

    // Atualizar indicador
    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const { strength, feedback } = checkPasswordStrength(password);

        const fill = strengthIndicator.querySelector('.strength-bar-fill');
        const text = strengthIndicator.querySelector('.strength-text');

        // Atualizar barra
        fill.style.width = strength + '%';

        // Atualizar cor e texto
        if (strength < 40) {
            fill.style.backgroundColor = '#FF4757';
            text.textContent = 'Fraca';
            text.style.color = '#FF4757';
        } else if (strength < 70) {
            fill.style.backgroundColor = '#FFD302';
            text.textContent = 'Média';
            text.style.color = '#B88400';
        } else {
            fill.style.backgroundColor = '#35D16C';
            text.textContent = 'Forte';
            text.style.color = '#0B4338';
        }

        // Mostrar dicas
        if (feedback.length > 0 && password.length > 0) {
            text.textContent += ': ' + feedback.join(', ');
        }
    });
});