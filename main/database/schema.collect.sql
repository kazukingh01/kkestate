--
-- PostgreSQL database dump
--

-- Dumped from database version 16.1 (Debian 16.1-1.pgdg120+1)
-- Dumped by pg_dump version 16.1 (Debian 16.1-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_sys_updated(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_sys_updated() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.sys_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_sys_updated() OWNER TO postgres;

SET default_tablespace = '';

--
-- Name: estate_detail; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estate_detail (
    id_run bigint NOT NULL,
    id_key smallint NOT NULL,
    value text
);


ALTER TABLE public.estate_detail OWNER TO postgres;

SET default_table_access_method = heap;

--
-- Name: estate_main; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estate_main (
    id bigint NOT NULL,
    name text,
    url text NOT NULL,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.estate_main OWNER TO postgres;

--
-- Name: estate_main_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estate_main_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estate_main_id_seq OWNER TO postgres;

--
-- Name: estate_main_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estate_main_id_seq OWNED BY public.estate_main.id;


--
-- Name: estate_mst_key; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estate_mst_key (
    id smallint NOT NULL,
    id_cleaned smallint,
    name text NOT NULL,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.estate_mst_key OWNER TO postgres;

--
-- Name: estate_mst_key_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estate_mst_key_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estate_mst_key_id_seq OWNER TO postgres;

--
-- Name: estate_mst_key_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estate_mst_key_id_seq OWNED BY public.estate_mst_key.id;


--
-- Name: estate_run; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estate_run (
    id bigint NOT NULL,
    id_main bigint NOT NULL,
    is_success boolean DEFAULT false NOT NULL,
    is_ref boolean DEFAULT false NOT NULL,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.estate_run OWNER TO postgres;

--
-- Name: estate_run_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estate_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estate_run_id_seq OWNER TO postgres;

--
-- Name: estate_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estate_run_id_seq OWNED BY public.estate_run.id;


--
-- Name: estate_tmp; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estate_tmp (
    url text NOT NULL,
    is_checked boolean DEFAULT false NOT NULL,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.estate_tmp OWNER TO postgres;


--
-- Name: estate_tmp_pref; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estate_tmp_pref (
    url text NOT NULL,
    target_checked boolean,
    sys_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.estate_tmp_pref OWNER TO postgres;


--
-- Name: estate_main id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_main ALTER COLUMN id SET DEFAULT nextval('public.estate_main_id_seq'::regclass);


--
-- Name: estate_mst_key id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_mst_key ALTER COLUMN id SET DEFAULT nextval('public.estate_mst_key_id_seq'::regclass);


--
-- Name: estate_run id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_run ALTER COLUMN id SET DEFAULT nextval('public.estate_run_id_seq'::regclass);


--
-- Name: estate_detail estate_detail_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_detail
    ADD CONSTRAINT estate_detail_pkey PRIMARY KEY (id_run, id_key);
CREATE INDEX idx_estate_detail_0 ON public.estate_detail USING btree (id_run);
CREATE INDEX idx_estate_detail_1 ON public.estate_detail USING btree (id_key);
CREATE INDEX IF NOT EXISTS idx_estate_detail_spec1_run ON public.estate_detail USING btree (id_run) WHERE id_key = 1;


--
-- Name: estate_main estate_main_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_main
    ADD CONSTRAINT estate_main_pkey PRIMARY KEY (id);


--
-- Name: estate_main estate_main_url_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_main
    ADD CONSTRAINT estate_main_url_key UNIQUE (url);


--
-- Name: estate_mst_key estate_mst_key_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_mst_key
    ADD CONSTRAINT estate_mst_key_name_key UNIQUE (name);


--
-- Name: estate_mst_key estate_mst_key_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_mst_key
    ADD CONSTRAINT estate_mst_key_pkey PRIMARY KEY (id);


--
-- Name: estate_run estate_run_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estate_run
    ADD CONSTRAINT estate_run_pkey PRIMARY KEY (id);
CREATE INDEX idx_estate_run_0 ON public.estate_run (is_success);
CREATE INDEX idx_estate_run_1 ON public.estate_run (timestamp);
CREATE INDEX idx_estate_run_2 ON public.estate_run (id, is_success, timestamp);
CREATE INDEX idx_estate_run_3 ON public.estate_run (is_ref);
CREATE INDEX idx_estate_run_4 ON public.estate_run (is_success, is_ref);

--
-- Name: estate_detail trg_update_sys_estate_detail_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_estate_detail_0 BEFORE UPDATE ON public.estate_detail FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: estate_main trg_update_sys_estate_main_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_estate_main_0 BEFORE UPDATE ON public.estate_main FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: estate_mst_key trg_update_sys_estate_mst_key_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_estate_mst_key_0 BEFORE UPDATE ON public.estate_mst_key FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: estate_tmp trg_update_sys_estate_tmp_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_estate_tmp_0 BEFORE UPDATE ON public.estate_tmp FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- Name: estate_tmp_pref trg_update_sys_estate_tmp_pref_0; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_update_sys_estate_tmp_pref_0 BEFORE UPDATE ON public.estate_tmp_pref FOR EACH ROW EXECUTE FUNCTION public.update_sys_updated();


--
-- PostgreSQL database dump complete
--

