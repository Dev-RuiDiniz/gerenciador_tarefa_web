document.addEventListener('DOMContentLoaded', function() {
    // Adicionar um ouvinte de evento para todas as formas de exclusão
    document.querySelectorAll('form[action$="/delete"]').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            // Previne o envio padrão do formulário
            event.preventDefault();

            // Exibe um popup de confirmação
            if (confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.')) {
                // Se o usuário confirmar, envia o formulário
                this.submit();
            }
        });
    });

    // Opcional: Adicionar funcionalidade para esconder mensagens flash após alguns segundos
    const flashMessages = document.querySelectorAll('.flashes li');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease-out';
            setTimeout(function() {
                message.remove();
            }, 500); // Remove o elemento após a transição
        }, 5000); // Mensagem desaparece após 5 segundos
    });
});