USE XUOSA_DB;

DELIMITER $$

CREATE PROCEDURE check_old_unclaimed_tickets()
BEGIN
    CREATE TEMPORARY TABLE updated_tickets (ticket_id INT, student_id INT);

    INSERT INTO updated_tickets (ticket_id, student_id)
    SELECT ticket_id, student_id
    FROM evs_ticket
    WHERE 
        id_not_claimed_violation = 0 AND 
        id_status = 0 AND 
        DATE(date_created) < CURDATE();

    UPDATE evs_ticket
    SET id_not_claimed_violation = 1
    WHERE ticket_id IN (SELECT ticket_id FROM updated_tickets);

    INSERT INTO evs_studentviolation (
        student_id,
        violation_id,
        count,
        community_service,
        community_service_status,
        apology_letter,
        apology_letter_status
    )
    SELECT 
        ut.student_id,
        4,
        1,
        FALSE,
        0,
        FALSE,
        0
    FROM updated_tickets ut
    ON DUPLICATE KEY UPDATE
        count = count + 1;

    DROP TEMPORARY TABLE updated_tickets;
END $$

DELIMITER ;

CREATE EVENT auto_mark_id_not_claimed
ON SCHEDULE EVERY 1 DAY
STARTS NOW()
DO
    CALL check_old_unclaimed_tickets();