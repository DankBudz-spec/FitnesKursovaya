--
-- PostgreSQL database dump
--

\restrict guKEpMKW8oIs9UFVvQSX2HkU4ddiFfcOByShYoASgYG7dtad9EZj0lpdj9bKKgZ

-- Dumped from database version 17.9
-- Dumped by pg_dump version 17.7

-- Started on 2026-04-27 19:40:26 UTC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 236 (class 1259 OID 17647)
-- Name: attendance_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance_log (
    visit_id integer NOT NULL,
    client_id integer NOT NULL,
    entry_dt timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    exit_dt timestamp without time zone,
    CONSTRAINT check_visit_time CHECK (((exit_dt IS NULL) OR (exit_dt > entry_dt)))
);


ALTER TABLE public.attendance_log OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 17646)
-- Name: attendance_log_visit_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_log_visit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_log_visit_id_seq OWNER TO postgres;

--
-- TOC entry 3571 (class 0 OID 0)
-- Dependencies: 235
-- Name: attendance_log_visit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_log_visit_id_seq OWNED BY public.attendance_log.visit_id;


--
-- TOC entry 234 (class 1259 OID 17626)
-- Name: class_registrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.class_registrations (
    registration_id integer NOT NULL,
    schedule_id integer NOT NULL,
    client_id integer NOT NULL,
    registration_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status text DEFAULT 'Записан'::text NOT NULL
);


ALTER TABLE public.class_registrations OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 17625)
-- Name: class_registrations_registration_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.class_registrations_registration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.class_registrations_registration_id_seq OWNER TO postgres;

--
-- TOC entry 3572 (class 0 OID 0)
-- Dependencies: 233
-- Name: class_registrations_registration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.class_registrations_registration_id_seq OWNED BY public.class_registrations.registration_id;


--
-- TOC entry 224 (class 1259 OID 17543)
-- Name: classes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classes (
    class_type_id integer NOT NULL,
    name text NOT NULL,
    description text
);


ALTER TABLE public.classes OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 17542)
-- Name: classes_class_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.classes_class_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.classes_class_type_id_seq OWNER TO postgres;

--
-- TOC entry 3573 (class 0 OID 0)
-- Dependencies: 223
-- Name: classes_class_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.classes_class_type_id_seq OWNED BY public.classes.class_type_id;


--
-- TOC entry 230 (class 1259 OID 17582)
-- Name: client_subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client_subscriptions (
    subscription_id integer NOT NULL,
    client_id integer NOT NULL,
    type_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    remaining_freeze_days integer DEFAULT 30 NOT NULL,
    is_blocked integer DEFAULT 0 NOT NULL,
    CONSTRAINT check_dates CHECK ((end_date >= start_date)),
    CONSTRAINT client_subscriptions_is_blocked_check CHECK ((is_blocked = ANY (ARRAY[0, 1])))
);


ALTER TABLE public.client_subscriptions OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 17581)
-- Name: client_subscriptions_subscription_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_subscriptions_subscription_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.client_subscriptions_subscription_id_seq OWNER TO postgres;

--
-- TOC entry 3574 (class 0 OID 0)
-- Dependencies: 229
-- Name: client_subscriptions_subscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_subscriptions_subscription_id_seq OWNED BY public.client_subscriptions.subscription_id;


--
-- TOC entry 220 (class 1259 OID 17511)
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    client_id integer NOT NULL,
    full_name text NOT NULL,
    phone_primary text NOT NULL,
    phone_secondary text,
    email text,
    birth_date date NOT NULL,
    address text,
    registration_date date DEFAULT CURRENT_DATE NOT NULL,
    medical_notes text,
    photo_path text,
    login text,
    password_hash text,
    CONSTRAINT check_age CHECK ((birth_date <= (CURRENT_DATE - '14 years'::interval)))
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 17510)
-- Name: clients_client_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clients_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clients_client_id_seq OWNER TO postgres;

--
-- TOC entry 3575 (class 0 OID 0)
-- Dependencies: 219
-- Name: clients_client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clients_client_id_seq OWNED BY public.clients.client_id;


--
-- TOC entry 228 (class 1259 OID 17567)
-- Name: equipment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equipment (
    equipment_id integer NOT NULL,
    zone_id integer NOT NULL,
    name text NOT NULL,
    purchase_date date NOT NULL,
    last_service_date date,
    status text DEFAULT 'Исправно'::text NOT NULL
);


ALTER TABLE public.equipment OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 17566)
-- Name: equipment_equipment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equipment_equipment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.equipment_equipment_id_seq OWNER TO postgres;

--
-- TOC entry 3576 (class 0 OID 0)
-- Dependencies: 227
-- Name: equipment_equipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equipment_equipment_id_seq OWNED BY public.equipment.equipment_id;


--
-- TOC entry 218 (class 1259 OID 17499)
-- Name: membership_types; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.membership_types (
    type_id integer NOT NULL,
    title text NOT NULL,
    price numeric(10,2) NOT NULL,
    duration_days integer NOT NULL,
    access_level integer NOT NULL,
    CONSTRAINT membership_types_price_check CHECK ((price > (0)::numeric))
);


ALTER TABLE public.membership_types OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 17498)
-- Name: membership_types_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.membership_types_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.membership_types_type_id_seq OWNER TO postgres;

--
-- TOC entry 3577 (class 0 OID 0)
-- Dependencies: 217
-- Name: membership_types_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.membership_types_type_id_seq OWNED BY public.membership_types.type_id;


--
-- TOC entry 238 (class 1259 OID 17661)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    payment_id integer NOT NULL,
    client_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    payment_method text NOT NULL,
    CONSTRAINT payments_amount_check CHECK ((amount > (0)::numeric))
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 17660)
-- Name: payments_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_payment_id_seq OWNER TO postgres;

--
-- TOC entry 3578 (class 0 OID 0)
-- Dependencies: 237
-- Name: payments_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_payment_id_seq OWNED BY public.payments.payment_id;


--
-- TOC entry 232 (class 1259 OID 17603)
-- Name: schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schedule (
    schedule_id integer NOT NULL,
    class_type_id integer NOT NULL,
    coach_id integer NOT NULL,
    zone_id integer NOT NULL,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone NOT NULL,
    CONSTRAINT check_times CHECK ((end_time > start_time))
);


ALTER TABLE public.schedule OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 17602)
-- Name: schedule_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.schedule_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_schedule_id_seq OWNER TO postgres;

--
-- TOC entry 3579 (class 0 OID 0)
-- Dependencies: 231
-- Name: schedule_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.schedule_schedule_id_seq OWNED BY public.schedule.schedule_id;


--
-- TOC entry 222 (class 1259 OID 17528)
-- Name: staff; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.staff (
    staff_id integer NOT NULL,
    full_name text NOT NULL,
    "position" text NOT NULL,
    specialization text NOT NULL,
    salary_rate numeric(10,2) NOT NULL,
    phone text NOT NULL,
    hire_date date DEFAULT CURRENT_DATE NOT NULL,
    login text,
    password_hash text,
    CONSTRAINT staff_salary_rate_check CHECK ((salary_rate >= (0)::numeric))
);


ALTER TABLE public.staff OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 17527)
-- Name: staff_staff_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.staff_staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.staff_staff_id_seq OWNER TO postgres;

--
-- TOC entry 3580 (class 0 OID 0)
-- Dependencies: 221
-- Name: staff_staff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.staff_staff_id_seq OWNED BY public.staff.staff_id;


--
-- TOC entry 226 (class 1259 OID 17554)
-- Name: zones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zones (
    zone_id integer NOT NULL,
    name text NOT NULL,
    capacity integer NOT NULL,
    required_access_level integer DEFAULT 1 NOT NULL,
    CONSTRAINT zones_capacity_check CHECK ((capacity > 0))
);


ALTER TABLE public.zones OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 17553)
-- Name: zones_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zones_zone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zones_zone_id_seq OWNER TO postgres;

--
-- TOC entry 3581 (class 0 OID 0)
-- Dependencies: 225
-- Name: zones_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zones_zone_id_seq OWNED BY public.zones.zone_id;


--
-- TOC entry 3338 (class 2604 OID 17650)
-- Name: attendance_log visit_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_log ALTER COLUMN visit_id SET DEFAULT nextval('public.attendance_log_visit_id_seq'::regclass);


--
-- TOC entry 3335 (class 2604 OID 17629)
-- Name: class_registrations registration_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_registrations ALTER COLUMN registration_id SET DEFAULT nextval('public.class_registrations_registration_id_seq'::regclass);


--
-- TOC entry 3326 (class 2604 OID 17546)
-- Name: classes class_type_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes ALTER COLUMN class_type_id SET DEFAULT nextval('public.classes_class_type_id_seq'::regclass);


--
-- TOC entry 3331 (class 2604 OID 17585)
-- Name: client_subscriptions subscription_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_subscriptions ALTER COLUMN subscription_id SET DEFAULT nextval('public.client_subscriptions_subscription_id_seq'::regclass);


--
-- TOC entry 3322 (class 2604 OID 17514)
-- Name: clients client_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients ALTER COLUMN client_id SET DEFAULT nextval('public.clients_client_id_seq'::regclass);


--
-- TOC entry 3329 (class 2604 OID 17570)
-- Name: equipment equipment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment ALTER COLUMN equipment_id SET DEFAULT nextval('public.equipment_equipment_id_seq'::regclass);


--
-- TOC entry 3321 (class 2604 OID 17502)
-- Name: membership_types type_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_types ALTER COLUMN type_id SET DEFAULT nextval('public.membership_types_type_id_seq'::regclass);


--
-- TOC entry 3340 (class 2604 OID 17664)
-- Name: payments payment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN payment_id SET DEFAULT nextval('public.payments_payment_id_seq'::regclass);


--
-- TOC entry 3334 (class 2604 OID 17606)
-- Name: schedule schedule_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule ALTER COLUMN schedule_id SET DEFAULT nextval('public.schedule_schedule_id_seq'::regclass);


--
-- TOC entry 3324 (class 2604 OID 17531)
-- Name: staff staff_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff ALTER COLUMN staff_id SET DEFAULT nextval('public.staff_staff_id_seq'::regclass);


--
-- TOC entry 3327 (class 2604 OID 17557)
-- Name: zones zone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones ALTER COLUMN zone_id SET DEFAULT nextval('public.zones_zone_id_seq'::regclass);


--
-- TOC entry 3563 (class 0 OID 17647)
-- Dependencies: 236
-- Data for Name: attendance_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance_log (visit_id, client_id, entry_dt, exit_dt) FROM stdin;
1	1	2026-04-26 10:00:00	2026-04-26 12:00:00
2	3	2026-04-25 09:00:00	2026-04-25 11:00:00
3	2	2026-04-27 14:00:00	2026-04-27 15:30:00
4	4	2026-04-27 19:00:00	\N
\.


--
-- TOC entry 3561 (class 0 OID 17626)
-- Dependencies: 234
-- Data for Name: class_registrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class_registrations (registration_id, schedule_id, client_id, registration_time, status) FROM stdin;
1	1	1	2026-04-27 13:58:47.24881	Записан
2	2	4	2026-04-27 13:58:47.24881	Записан
3	1	2	2026-04-27 13:58:47.24881	Отменено
9	3	1	2026-04-27 17:56:44.100338	Записан
8	3	1	2026-04-27 18:04:05.580513	Записан
\.


--
-- TOC entry 3551 (class 0 OID 17543)
-- Dependencies: 224
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classes (class_type_id, name, description) FROM stdin;
1	Йога	Растяжка и дыхательные практики
2	Бокс	Тренировка в зале единоборств
3	Бассейн	Свободное плавание и аквааэробика
4	Кроссфит	Высокоинтенсивная функциональная тренировка
5	Пилатес	Укрепление мышц спины и кора
\.


--
-- TOC entry 3557 (class 0 OID 17582)
-- Dependencies: 230
-- Data for Name: client_subscriptions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.client_subscriptions (subscription_id, client_id, type_id, start_date, end_date, remaining_freeze_days, is_blocked) FROM stdin;
1	1	3	2026-01-01	2026-12-31	30	0
2	2	1	2026-04-10	2026-05-10	30	0
4	4	2	2026-04-15	2026-05-15	30	0
5	5	1	2026-04-27	2026-05-27	30	0
3	3	4	2026-03-01	2026-06-11	5	0
\.


--
-- TOC entry 3547 (class 0 OID 17511)
-- Dependencies: 220
-- Data for Name: clients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.clients (client_id, full_name, phone_primary, phone_secondary, email, birth_date, address, registration_date, medical_notes, photo_path, login, password_hash) FROM stdin;
1	Смирнов Андрей Викторович	89112223344	\N	smirnov@mail.ru	1990-05-15	\N	2022-01-01	Здоров	\N	client_smirnov	hash6
2	Новиков Иван Андреевич	89550001122	\N	novikov@yandex.ru	2008-11-20	\N	2026-04-27	Травма плеча	\N	client_novikov	hash7
3	Петрова Анна Николаевна	89223334455	\N	petrova@gmail.com	1995-03-10	\N	2024-10-12	Аллергия	\N	client_petrova	hash8
4	Волков Дмитрий Олегович	89334445566	\N	volkov@bk.ru	1985-07-25	\N	2023-06-01	\N	\N	client_volkov	hash9
5	ДОЛЖНИКОВ Игорь	89990000000	\N	bad@mail.ru	1992-01-01	\N	2026-03-01	Специальный клиент для теста	\N	debtor	hash10
\.


--
-- TOC entry 3555 (class 0 OID 17567)
-- Dependencies: 228
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.equipment (equipment_id, zone_id, name, purchase_date, last_service_date, status) FROM stdin;
1	1	Беговая дорожка Matrix	2024-05-10	2026-04-27	Исправно
3	3	Система фильтрации	2023-08-20	2026-04-27	Исправно
4	4	Коврики для йоги	2025-01-15	2026-04-27	Исправно
2	2	Боксерский мешок кожаный	2024-12-01	2025-10-10	Исправно
\.


--
-- TOC entry 3545 (class 0 OID 17499)
-- Dependencies: 218
-- Data for Name: membership_types; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.membership_types (type_id, title, price, duration_days, access_level) FROM stdin;
1	Базовый месяц	3000.00	30	1
2	Дневной стандарт	2500.00	30	1
3	Годовой VIP	25000.00	365	3
4	Студенческий квартал	7000.00	90	1
5	Семейный безлимит	45000.00	365	2
\.


--
-- TOC entry 3565 (class 0 OID 17661)
-- Dependencies: 238
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (payment_id, client_id, amount, payment_date, payment_method) FROM stdin;
1	1	25000.00	2026-04-27 13:58:47.24881	Карта
2	2	3000.00	2026-04-27 13:58:47.24881	Наличные
3	3	7000.00	2026-04-27 13:58:47.24881	QR-код
4	4	2500.00	2026-04-27 13:58:47.24881	Карта
\.


--
-- TOC entry 3559 (class 0 OID 17603)
-- Dependencies: 232
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.schedule (schedule_id, class_type_id, coach_id, zone_id, start_time, end_time) FROM stdin;
1	1	2	4	2026-04-27 09:00:00	2026-04-27 10:30:00
2	2	3	2	2026-04-27 18:00:00	2026-04-27 19:00:00
3	3	2	3	2026-04-28 10:00:00	2026-04-28 11:30:00
\.


--
-- TOC entry 3549 (class 0 OID 17528)
-- Dependencies: 222
-- Data for Name: staff; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.staff (staff_id, full_name, "position", specialization, salary_rate, phone, hire_date, login, password_hash) FROM stdin;
1	Надеин Виталий Сергеевич	Администратор	Управление	1500.00	89000000000	2023-01-01	admin	admin
2	Соколова Дарья Сергеевна	Тренер	Йога, пилатес	1200.00	89001112233	2023-01-15	sokolova	hash5
3	Иванов Петр Сергеевич	Тренер	Бокс	1000.00	89005556677	2024-02-01	ivanov	hash4
4	Бузина Ольга Петровна	Менеджер	Продажи	800.00	89007778899	2025-01-10	buzina	hash3
\.


--
-- TOC entry 3553 (class 0 OID 17554)
-- Dependencies: 226
-- Data for Name: zones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zones (zone_id, name, capacity, required_access_level) FROM stdin;
1	Тренажерный зал	40	1
2	Зал единоборств	15	2
3	Аква-зона	20	3
4	Зал групповых программ	25	1
5	Кардио-зона	15	1
\.


--
-- TOC entry 3582 (class 0 OID 0)
-- Dependencies: 235
-- Name: attendance_log_visit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_log_visit_id_seq', 4, true);


--
-- TOC entry 3583 (class 0 OID 0)
-- Dependencies: 233
-- Name: class_registrations_registration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_registrations_registration_id_seq', 9, true);


--
-- TOC entry 3584 (class 0 OID 0)
-- Dependencies: 223
-- Name: classes_class_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.classes_class_type_id_seq', 5, true);


--
-- TOC entry 3585 (class 0 OID 0)
-- Dependencies: 229
-- Name: client_subscriptions_subscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.client_subscriptions_subscription_id_seq', 5, true);


--
-- TOC entry 3586 (class 0 OID 0)
-- Dependencies: 219
-- Name: clients_client_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clients_client_id_seq', 5, true);


--
-- TOC entry 3587 (class 0 OID 0)
-- Dependencies: 227
-- Name: equipment_equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_equipment_id_seq', 4, true);


--
-- TOC entry 3588 (class 0 OID 0)
-- Dependencies: 217
-- Name: membership_types_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.membership_types_type_id_seq', 5, true);


--
-- TOC entry 3589 (class 0 OID 0)
-- Dependencies: 237
-- Name: payments_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_payment_id_seq', 4, true);


--
-- TOC entry 3590 (class 0 OID 0)
-- Dependencies: 231
-- Name: schedule_schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.schedule_schedule_id_seq', 3, true);


--
-- TOC entry 3591 (class 0 OID 0)
-- Dependencies: 221
-- Name: staff_staff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.staff_staff_id_seq', 4, true);


--
-- TOC entry 3592 (class 0 OID 0)
-- Dependencies: 225
-- Name: zones_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zones_zone_id_seq', 5, true);


--
-- TOC entry 3386 (class 2606 OID 17654)
-- Name: attendance_log attendance_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_log
    ADD CONSTRAINT attendance_log_pkey PRIMARY KEY (visit_id);


--
-- TOC entry 3384 (class 2606 OID 17635)
-- Name: class_registrations class_registrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_registrations
    ADD CONSTRAINT class_registrations_pkey PRIMARY KEY (registration_id);


--
-- TOC entry 3370 (class 2606 OID 17552)
-- Name: classes classes_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_name_key UNIQUE (name);


--
-- TOC entry 3372 (class 2606 OID 17550)
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (class_type_id);


--
-- TOC entry 3380 (class 2606 OID 17591)
-- Name: client_subscriptions client_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_subscriptions
    ADD CONSTRAINT client_subscriptions_pkey PRIMARY KEY (subscription_id);


--
-- TOC entry 3356 (class 2606 OID 17524)
-- Name: clients clients_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_email_key UNIQUE (email);


--
-- TOC entry 3358 (class 2606 OID 17526)
-- Name: clients clients_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_login_key UNIQUE (login);


--
-- TOC entry 3360 (class 2606 OID 17522)
-- Name: clients clients_phone_primary_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_phone_primary_key UNIQUE (phone_primary);


--
-- TOC entry 3362 (class 2606 OID 17520)
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (client_id);


--
-- TOC entry 3378 (class 2606 OID 17575)
-- Name: equipment equipment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_pkey PRIMARY KEY (equipment_id);


--
-- TOC entry 3352 (class 2606 OID 17507)
-- Name: membership_types membership_types_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_types
    ADD CONSTRAINT membership_types_pkey PRIMARY KEY (type_id);


--
-- TOC entry 3354 (class 2606 OID 17509)
-- Name: membership_types membership_types_title_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.membership_types
    ADD CONSTRAINT membership_types_title_key UNIQUE (title);


--
-- TOC entry 3388 (class 2606 OID 17670)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (payment_id);


--
-- TOC entry 3382 (class 2606 OID 17609)
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (schedule_id);


--
-- TOC entry 3364 (class 2606 OID 17541)
-- Name: staff staff_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_login_key UNIQUE (login);


--
-- TOC entry 3366 (class 2606 OID 17539)
-- Name: staff staff_phone_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_phone_key UNIQUE (phone);


--
-- TOC entry 3368 (class 2606 OID 17537)
-- Name: staff staff_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (staff_id);


--
-- TOC entry 3374 (class 2606 OID 17565)
-- Name: zones zones_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_name_key UNIQUE (name);


--
-- TOC entry 3376 (class 2606 OID 17563)
-- Name: zones zones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_pkey PRIMARY KEY (zone_id);


--
-- TOC entry 3397 (class 2606 OID 17655)
-- Name: attendance_log attendance_log_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance_log
    ADD CONSTRAINT attendance_log_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 3395 (class 2606 OID 17641)
-- Name: class_registrations class_registrations_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_registrations
    ADD CONSTRAINT class_registrations_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 3396 (class 2606 OID 17636)
-- Name: class_registrations class_registrations_schedule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.class_registrations
    ADD CONSTRAINT class_registrations_schedule_id_fkey FOREIGN KEY (schedule_id) REFERENCES public.schedule(schedule_id) ON DELETE CASCADE;


--
-- TOC entry 3390 (class 2606 OID 17592)
-- Name: client_subscriptions client_subscriptions_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_subscriptions
    ADD CONSTRAINT client_subscriptions_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 3391 (class 2606 OID 17597)
-- Name: client_subscriptions client_subscriptions_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client_subscriptions
    ADD CONSTRAINT client_subscriptions_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.membership_types(type_id) ON DELETE CASCADE;


--
-- TOC entry 3389 (class 2606 OID 17576)
-- Name: equipment equipment_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equipment
    ADD CONSTRAINT equipment_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(zone_id) ON DELETE CASCADE;


--
-- TOC entry 3398 (class 2606 OID 17671)
-- Name: payments payments_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id) ON DELETE CASCADE;


--
-- TOC entry 3392 (class 2606 OID 17610)
-- Name: schedule schedule_class_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_class_type_id_fkey FOREIGN KEY (class_type_id) REFERENCES public.classes(class_type_id) ON DELETE CASCADE;


--
-- TOC entry 3393 (class 2606 OID 17615)
-- Name: schedule schedule_coach_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_coach_id_fkey FOREIGN KEY (coach_id) REFERENCES public.staff(staff_id) ON DELETE CASCADE;


--
-- TOC entry 3394 (class 2606 OID 17620)
-- Name: schedule schedule_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(zone_id) ON DELETE CASCADE;


-- Completed on 2026-04-27 19:40:26 UTC

--
-- PostgreSQL database dump complete
--

\unrestrict guKEpMKW8oIs9UFVvQSX2HkU4ddiFfcOByShYoASgYG7dtad9EZj0lpdj9bKKgZ

