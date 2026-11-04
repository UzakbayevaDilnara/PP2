CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names VARCHAR[],
    p_phones VARCHAR[],
    INOUT invalid_data TEXT DEFAULT ''
)
LANGUAGE plpgsql AS $$
DECLARE
    i INTEGER;
    v_name VARCHAR;
    v_phone VARCHAR;
BEGIN
    FOR i IN 1..array_length(p_names, 1) LOOP
        v_name := p_names[i];
        v_phone := p_phones[i];

        IF v_phone ~ '^[0-9]{10,15}$' THEN
            IF EXISTS (SELECT 1 FROM phonebook WHERE phone = v_phone) THEN
                UPDATE phonebook SET name = v_name WHERE phone = v_phone;
            ELSE
                INSERT INTO phonebook(name, phone) VALUES(v_name, v_phone);
            END IF;
        ELSE
            invalid_data := invalid_data || v_name || ' (' || v_phone || '); ';
        END IF;
    END LOOP;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_name VARCHAR DEFAULT NULL, p_phone VARCHAR DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM phonebook WHERE name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM phonebook WHERE phone = p_phone;
    ELSE
        RAISE EXCEPTION 'Аты немесе телефонды көрсету керек!';
    END IF;
END;
$$;
