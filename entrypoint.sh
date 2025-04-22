#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput

mysql -h "$DB_HOST" -u "root" -p"$DB_ROOT_PASSWORD" "$DB_NAME" <<EOF

INSERT INTO EVS_semester
VALUES (1, 'First Semester'), (2, 'Second Semester'), (3, 'Intersession');

INSERT INTO EVS_violation
VALUES
(1, 'Uniform Violation'),
(2, 'Dress Code Violation'),
(3, 'ID Violation'),
(4, 'ID Not Claimed');

INSERT INTO EVS_reason VALUES
(1, 'ID', 'Forgotten or misplaced', '#E74C3C'),
(2, 'ID', 'ID not claimed on time', '#F39C12'),
(3, 'Uniform', 'Lack of Awareness of Specific Policy', '#F7D358'),
(4, 'Uniform', 'Unforeseen Circumstances', '#A9DFBF'),
(5, 'Uniform', 'Misinterpretation of dress code compliance', '#229954'),
(6, 'Uniform', 'Substitution of footwear (Unexpected damage/unavailability)', '#34495E'),
(7, 'DressCode', 'Unawareness of mandated garment length requirements', '#5DADE2'),
(8, 'DressCode', 'Oversight in compliance', '#A569BD'),
(9, 'DressCode', 'Personal style preference conflicting with policy', '#F5B7B1'),
(10, 'DressCode', 'Temporary use of restricted footwear due to convenience or necessity', '#B2BABB');

DELIMITER //

CREATE PROCEDURE check_old_unclaimed_tickets()
BEGIN
    CREATE TEMPORARY TABLE updated_tickets (
        ticket_id INT,
        student_id INT,
        acad_year_id INT,
        ticket_status INT,
        id_violation TINYINT,
        dress_code_violation TINYINT,
        uniform_violation TINYINT
    );

    INSERT INTO updated_tickets (ticket_id, student_id, acad_year_id, ticket_status, id_violation, dress_code_violation, uniform_violation)
    SELECT 
        ticket_id, student_id, acad_year_id, ticket_status,
        id_violation, dress_code_violation, uniform_violation
    FROM EVS_ticket
    WHERE 
        id_not_claimed_violation = 0 AND 
        id_status = 0 AND 
        DATE(date_created) < CURDATE();

    UPDATE EVS_ticket
    SET id_not_claimed_violation = 1,
        ticket_status = 0
    WHERE ticket_id IN (SELECT ticket_id FROM updated_tickets);

    UPDATE EVS_studentviolation sv
    JOIN updated_tickets ut 
        ON sv.student_id = ut.student_id AND sv.acad_year_id = ut.acad_year_id
    SET sv.count = sv.count - 1
    WHERE ut.ticket_status IN (1, 2)
      AND ut.id_violation = 1
      AND ut.dress_code_violation = 0
      AND ut.uniform_violation = 0
      AND sv.violation_id = 1
      AND sv.count > 0;

    DELETE FROM EVS_studentviolation WHERE count = 0;

    UPDATE EVS_studentviolation sv
    JOIN updated_tickets ut 
        ON sv.student_id = ut.student_id AND sv.acad_year_id = ut.acad_year_id
    SET sv.count = sv.count - 1
    WHERE ut.ticket_status IN (1, 2)
      AND ut.dress_code_violation = 1
      AND sv.violation_id = 2
      AND sv.count > 0;

    DELETE FROM EVS_studentviolation WHERE count = 0;

    UPDATE EVS_studentviolation sv
    JOIN updated_tickets ut 
        ON sv.student_id = ut.student_id AND sv.acad_year_id = ut.acad_year_id
    SET sv.count = sv.count - 1
    WHERE ut.ticket_status IN (1, 2)
      AND ut.uniform_violation = 1
      AND sv.violation_id = 3
      AND sv.count > 0;

    DELETE FROM EVS_studentviolation WHERE count = 0;

    DROP TEMPORARY TABLE updated_tickets;
END //

DELIMITER ;

SET GLOBAL event_scheduler = ON;

CREATE EVENT IF NOT EXISTS auto_mark_id_not_claimed
ON SCHEDULE EVERY 1 DAY
STARTS NOW()
DO
    CALL check_old_unclaimed_tickets();

EOF

echo "Database initialized."

python -m gunicorn --bind 0.0.0.0:8001 --workers 3 XUOSA_EVS.wsgi:application

#python manage.py runserver 0.0.0.0:8000