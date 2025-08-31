CREATE TABLE IF NOT EXISTS `dispositivos` (
    `mac` VARCHAR(20) NOT NULL, 
    `local` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`mac`),
    UNIQUE KEY `local` (`local`)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `usuarios` (
    `id` CHAR(8) NOT NULL UNIQUE,
    `nome` VARCHAR(100) NOT NULL,
    `alias` VARCHAR(11) NOT NULL,
    `cpf` VARCHAR(14) NOT NULL UNIQUE CHECK (`cpf` REGEXP '^[0-9]{3}\\.[0-9]{3}\\.[0-9]{3}-[0-9]{2}$'),
    `email` VARCHAR(255) UNIQUE NOT NULL CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),  
    `matricula` VARCHAR(255),
    `senha` CHAR(64),
    `icon_path` VARCHAR(255) DEFAULT NULL,
    `permission_level` ENUM('discente', 'docente', 'administrador') NOT NULL DEFAULT 'discente',
    `encodings` TEXT NOT NULL,
   
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `historico` (
    `nome` VARCHAR(100) NOT NULL,
    `alias` VARCHAR(11) NOT NULL,
    `id` CHAR(8), 
    `email` VARCHAR(255) NOT NULL,
    `matricula` VARCHAR(255),
    `permission_level` ENUM('discente', 'docente', 'administrador') NOT NULL DEFAULT 'discente',  
    `mac` VARCHAR(20) DEFAULT NULL,  
    `ip` VARCHAR(15) NOT NULL,  
    `local` VARCHAR(100) DEFAULT NULL,  
    `trust` INT NOT NULL CHECK (`trust` BETWEEN 0 AND 100),  
    `data_acesso` DATE,  
    `horario_acesso` TIME, 
    `log` TEXT DEFAULT NULL,
    KEY `mac` (`mac`),
    KEY `local` (`local`),
    KEY `email` (`email`),
    CONSTRAINT `historico_ibfk_1` FOREIGN KEY (`mac`) REFERENCES `dispositivos` (`mac`) ON DELETE SET NULL,
    CONSTRAINT `historico_ibfk_2` FOREIGN KEY (`local`) REFERENCES `dispositivos` (`local`) ON DELETE SET NULL,
    CONSTRAINT `historico_ibfk_3` FOREIGN KEY (`id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
    CONSTRAINT `historico_ibfk_4` FOREIGN KEY (`email`) REFERENCES `usuarios` (`email`) ON DELETE CASCADE,
    CONSTRAINT `historico_chk_3` CHECK (
        REGEXP_LIKE(`ip`, '^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    )
) ENGINE = InnoDB;

DELIMITER //
CREATE TRIGGER before_update_usuarios
BEFORE UPDATE ON usuarios
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

-- Inserir usuário administrador root (com ID manual)
INSERT INTO usuarios (cpf, nome, alias, email, matricula, senha, permission_level, encodings, id, icon_path) 
VALUES ('000.000.000-00', 'root', 'root', 'root.debug@gmail.com', '123456', 'b0622dd2afbf791c668aa869409a4671113a9606c24afb8e409836bfdcb2c0c2', 'administrador', '0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0', '00000001', '');

-- Dispositivo de teste
INSERT INTO dispositivos (mac, local)
VALUES ('00:14:22:01:23:45', 'Laboratorio 1');

-- Registro no histórico
INSERT INTO historico (nome, alias, email, matricula, permission_level, mac, ip, local, trust, data_acesso, horario_acesso, id, log) 
SELECT nome, alias, email, matricula, permission_level, '00:14:22:01:23:45', '192.168.0.1', 'Laboratorio 1', 100, CURRENT_DATE, CURRENT_TIME, id, 'Apenas para debug esta row !' 
FROM usuarios WHERE id = '00000001';
