-- =========================================================
-- Tabela de dispositivos
-- Armazena informações sobre os dispositivos (ex.: câmeras, portas)
-- =========================================================
CREATE TABLE IF NOT EXISTS `<adicione o nome da tabela de dispositivos>` (
    `mac` VARCHAR(20) NOT NULL,         -- Endereço MAC do dispositivo
    `local` VARCHAR(255) NOT NULL,      -- Local físico do dispositivo
    PRIMARY KEY (`mac`),                -- MAC como chave primária
    UNIQUE KEY `local` (`local`)        -- Local deve ser único
) ENGINE = InnoDB;

-- =========================================================
-- Tabela de usuários
-- Armazena informações dos usuários do sistema
-- =========================================================
CREATE TABLE IF NOT EXISTS `<adicione o nome da tabela de usuarios>` (
    `id` CHAR(8) NOT NULL UNIQUE,       -- Identificador único do usuário
    `nome` VARCHAR(100) NOT NULL,       -- Nome completo
    `alias` VARCHAR(11) NOT NULL,       -- Nome de usuário / apelido
    `cpf` VARCHAR(14) NOT NULL UNIQUE CHECK (`cpf` REGEXP '^[0-9]{3}\\.[0-9]{3}\\.[0-9]{3}-[0-9]{2}$'), -- CPF válido
    `email` VARCHAR(255) UNIQUE NOT NULL CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'), -- E-mail válido
    `matricula` VARCHAR(255),           -- Número de matrícula
    `senha` CHAR(64),                   -- Senha (hash)
    `icon_path` VARCHAR(255) DEFAULT NULL, -- Caminho do ícone/avatar
    `permission_level` ENUM('discente', 'docente', 'administrador') NOT NULL DEFAULT 'discente', -- Nível de permissão
    `encodings` TEXT NOT NULL,           -- Dados de reconhecimento facial (codificação)
   
    PRIMARY KEY (`id`)                   -- ID como chave primária
) ENGINE=InnoDB;

-- =========================================================
-- Tabela de histórico
-- Armazena registros de acesso e ações dos usuários
-- =========================================================
CREATE TABLE IF NOT EXISTS `<adicione o nome da tabela de historico>` (
    `nome` VARCHAR(100) NOT NULL,        -- Nome do usuário
    `alias` VARCHAR(11) NOT NULL,        -- Alias do usuário
    `id` CHAR(8),                        -- ID do usuário (FK para tabela de usuarios)
    `email` VARCHAR(255) NOT NULL,       -- E-mail do usuário (FK para tabela de usuarios)
    `matricula` VARCHAR(255),            -- Matrícula
    `permission_level` ENUM('discente', 'docente', 'administrador') NOT NULL DEFAULT 'discente', -- Nível de permissão
    `mac` VARCHAR(20) DEFAULT NULL,      -- MAC do dispositivo usado (FK para tabela de dispositivos)
    `ip` VARCHAR(15) NOT NULL,           -- Endereço IP do acesso
    `local` VARCHAR(100) DEFAULT NULL,   -- Local do dispositivo usado (FK para tabela de dispositivos)
    `trust` INT NOT NULL CHECK (`trust` BETWEEN 0 AND 100), -- Nível de confiança da ação
    `data_acesso` DATE,                  -- Data do acesso
    `horario_acesso` TIME,               -- Horário do acesso
    `log` TEXT DEFAULT NULL,             -- Log de ação ou comentário
    KEY `mac` (`mac`),
    KEY `local` (`local`),
    KEY `email` (`email`),

    -- Relações com dispositivos e usuários
    CONSTRAINT `historico_ibfk_1` FOREIGN KEY (`mac`) REFERENCES `<adicione o nome da tabela de dispositivos>` (`mac`) ON DELETE SET NULL,
    CONSTRAINT `historico_ibfk_2` FOREIGN KEY (`local`) REFERENCES `<adicione o nome da tabela de dispositivos>` (`local`) ON DELETE SET NULL,
    CONSTRAINT `historico_ibfk_3` FOREIGN KEY (`id`) REFERENCES `<adicione o nome da tabela de usuarios>` (`id`) ON DELETE CASCADE,
    CONSTRAINT `historico_ibfk_4` FOREIGN KEY (`email`) REFERENCES `<adicione o nome da tabela de usuarios>` (`email`) ON DELETE CASCADE,

    -- Validação do IP
    CONSTRAINT `historico_chk_3` CHECK (
        REGEXP_LIKE(`ip`, '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    )
) ENGINE = InnoDB;

-- =========================================================
-- Trigger: before_update_usuarios
-- Garante que apenas usuários administradores podem ter senha e que ela não seja nula
-- =========================================================
DELIMITER //
CREATE TRIGGER before_update_usuarios
BEFORE UPDATE ON `<adicione o nome da tabela de usuarios>`
FOR EACH ROW
BEGIN
    IF NEW.permission_level = 'administrador' THEN
        IF NEW.senha IS NULL OR NEW.senha = '' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Usuários com permission_level = administrador devem ter uma senha.';
        END IF;
    ELSE
        IF NEW.senha IS NOT NULL AND NEW.senha <> '' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Apenas usuários administradores podem ter senha.';
        END IF;
    END IF;
END;
//
DELIMITER ;

-- =========================================================
-- Inserir usuário administrador root (com ID manual)

-- Senha padrão do usuario de DEBUG: admin123

-- TODO: retirar após adicionar o primeiro usuario é apenas desmonstração

-- =========================================================
INSERT INTO `<adicione o nome da tabela de usuarios>` (cpf, nome, alias, email, matricula, senha, permission_level, encodings, id, icon_path) 
VALUES ('000.000.000-00', 'root', 'root', 'root.debug@gmail.com', '123456', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'administrador', '0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0', '00000001', '');
