CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    IF p_type NOT IN ('home','work','mobile') THEN
        RAISE EXCEPTION 'Invalid phone type: %', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name)
        RETURNING id INTO v_group_id;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id       INTEGER,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phones   TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.name,
        c.email,
        c.birthday,
        g.name AS grp,
        COALESCE(
            STRING_AGG(DISTINCT p.phone || '(' || p.type || ')', ', '),
            ''
        ) AS phones
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE c.name    ILIKE '%' || p_query || '%'
       OR c.phone   ILIKE '%' || p_query || '%'
       OR c.email   ILIKE '%' || p_query || '%'
       OR p.phone   ILIKE '%' || p_query || '%'
    GROUP BY c.id, c.name, c.email, c.birthday, g.name
    ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION get_contacts_page(
    p_group       TEXT    DEFAULT NULL,
    p_email       TEXT    DEFAULT NULL,
    p_sort_by     TEXT    DEFAULT 'name',   -- name | birthday | created_at
    p_limit       INTEGER DEFAULT 5,
    p_offset      INTEGER DEFAULT 0
)
RETURNS TABLE (
    id         INTEGER,
    name       VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    grp        VARCHAR,
    created_at TIMESTAMP,
    phones     TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT c.id, c.name, c.email, c.birthday, g.name,
                c.created_at,
                COALESCE(STRING_AGG(DISTINCT p.phone || ''('' || p.type || '')'', '', ''), '''')
         FROM contacts c
         LEFT JOIN groups g ON g.id = c.group_id
         LEFT JOIN phones p ON p.contact_id = c.id
         WHERE ($1 IS NULL OR g.name = $1)
           AND ($2 IS NULL OR c.email ILIKE ''%%'' || $2 || ''%%'')
         GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
         ORDER BY %I
         LIMIT $3 OFFSET $4',
        CASE p_sort_by
            WHEN 'birthday'   THEN 'c.birthday'
            WHEN 'created_at' THEN 'c.created_at'
            ELSE 'c.name'
        END
    ) USING p_group, p_email, p_limit, p_offset;
END;
$$;
