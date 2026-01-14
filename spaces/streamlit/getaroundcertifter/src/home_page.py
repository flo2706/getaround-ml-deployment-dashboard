# main_page.py
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

from common import (
    COL_STATE,
    COL_CHECKIN,
    COL_DELAY_AT_CHECKOUT,
    COL_CAR_ID,
    COL_HAS_CONNECT,
    COL_CAR_TYPE,
    COLOR_CI,
    RESA_COLORS,
    ORDER_STATUS,
    COL_PRICE_PER_DAY,
    read_logo,
    apply_scope,
    state_pct,
    checkin_pct,
    checkout_counts,
    require_cols,
    get_plotly_theme,
    place_title as _place_title,
)

# Apply the shared Plotly theme
pio.templates["getaround"] = get_plotly_theme()
pio.templates.default = "getaround"


# Page
def main_page(dataset_pricing: pd.DataFrame, df_delay: pd.DataFrame) -> None:
    """ Home page of the dashboard — overall KPIs, behavior, pricing structure."""

    # Branding area (logo + title)
    svg = read_logo("getaround_logo.svg")
    if svg:
        st.markdown(
            f"<div style='text-align:center'>{svg}</div>", unsafe_allow_html=True
        )

    st.markdown(
        "<h1 style='text-align:center;'>Dashboard Getaround — Analyse & Prédiction</h1>",
        unsafe_allow_html=True
    )
    st.caption(
        f"Dernière mise à jour : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # Scope selection (once)
    scope = st.radio(
        "Portée des indicateurs",
        ["Toutes les voitures", "Connect uniquement", "Mobile uniquement"],
        horizontal=True
    )

    # Normalize columns + apply scope
    df_scoped, pricing_scoped = apply_scope(df_delay, dataset_pricing, scope)

    # Safety checks
    if df_scoped.empty:
        st.info("Aucune location disponible dans le périmètre sélectionné.")
        return
    if pricing_scoped.empty:
        st.info(
            "Aucun véhicule correspondant dans le fichier pricing pour ce périmètre."
        )
        return

    if not require_cols(
        df_scoped,
        {COL_STATE, COL_CHECKIN, COL_DELAY_AT_CHECKOUT, COL_CAR_ID},
        "df_delay (scope selected)"
    ):
        return

    if not require_cols(
        pricing_scoped, {COL_PRICE_PER_DAY}, "pricing (scope selected)"
    ):
        return

    # KPI Overview
    st.header("Quelques chiffres")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Nombre de locations (scope)", f"{len(df_scoped):,}")
        st.metric(
            "Voitures observées (delay, scope)", f"{df_scoped[COL_CAR_ID].nunique():,}"
        )

    with col2:
        if COL_HAS_CONNECT in pricing_scoped.columns:
            st.metric(
                "Voitures équipées Connect (scope)",
                f"{pricing_scoped[COL_HAS_CONNECT].mean() * 100:.1f} %"
            )
        st.metric(
            "Locations via Connect (scope)",
            f"{df_scoped[COL_CHECKIN].eq('connect').mean() * 100:.1f} %"
        )

    with col3:
        # Use ended subset for delay KPIs
        df_ended = df_scoped[df_scoped[COL_STATE].eq("ended")].copy()
        s_delay = df_ended[COL_DELAY_AT_CHECKOUT]

        observed = s_delay.dropna()

        late_pct = observed.gt(0).mean() * 100 if len(observed) else 0.0
        ok_pct = observed.le(0).mean() * 100 if len(observed) else 0.0
        missing_pct = s_delay.isna().mean() * 100 if len(s_delay) else 0.0

        st.metric("Retours en retard (parmi observés ended)", f"{late_pct:.1f} %")
        st.metric("À l'heure / en avance (parmi observés ended)", f"{ok_pct:.1f} %")
        st.caption(f"Non renseigné (ended) : {missing_pct:.1f} %")

    st.markdown("---")

    # Behavior analysis (4 charts)
    height = 340

    # A — booking completion status (100% stacked bar)
    state_data = state_pct(df_scoped).copy()  # ['Statut de réservation', 'Pourcentage']
    if not state_data.empty:
        state_data["Catégorie"] = "Réservations"
        fig_a = px.bar(
            state_data,
            x="Catégorie",  # single bar
            y="Pourcentage",
            color="Statut de réservation",
            text="Pourcentage",
            barmode="stack",
            color_discrete_map=RESA_COLORS
        )
        fig_a.update_traces(texttemplate="%{y:.1f}%", textposition="inside")
        fig_a.update_layout(
            height=height,
            showlegend=True,
            yaxis=dict(range=[0, 100], title="Pourcentage"),
            xaxis_title=None,
            plot_bgcolor="white",
            legend_title_text="",
            legend=dict(orientation="h", y=-0.3)
        )
        _place_title(fig_a, "Réservations achevées vs annulées (100%)")
    else:
        fig_a = None

    # B — check-in modes (%)
    ci_data = checkin_pct(df_scoped)
    fig_b = px.bar(
        ci_data,
        x="Type de check-in",
        y="Pourcentage",
        color="Type de check-in",
        text="Pourcentage",
        color_discrete_map=COLOR_CI
    )
    fig_b.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    fig_b.update_layout(legend_title_text="", legend=dict(orientation="h", y=-0.2))
    fig_b.update_yaxes(
        range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix=" %"
    )
    _place_title(fig_b, "Répartition des modes de check-in (%)")

    # C/D — ended only for meaningful delay status
    df_for_counts = df_scoped[df_scoped[COL_STATE].eq("ended")].copy()
    counts = checkout_counts(df_for_counts)

    # C — return share by check-in type (%)
    fig_c = px.bar(
        counts,
        x="checkout_status",
        y="pct",
        color=COL_CHECKIN,
        barmode="group",
        category_orders={"checkout_status": ORDER_STATUS},
        text="pct",
        color_discrete_map=COLOR_CI,
        labels={"checkout_status": "Statut du départ", "pct": "Proportion (%)"}
    )
    fig_c.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_c.update_yaxes(
        range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix=" %"
    )
    fig_c.update_layout(legend_title_text="", legend=dict(orientation="h", y=-0.2))
    _place_title(fig_c, "Répartition (%) des retours selon le type de check-in")

    # D — return count by check-in type (n)
    fig_d = px.bar(
        counts,
        x="checkout_status",
        y="n",
        color=COL_CHECKIN,
        barmode="group",
        category_orders={"checkout_status": ORDER_STATUS},
        text="n",
        color_discrete_map=COLOR_CI,
        labels={"checkout_status": "Statut du départ", "n": "Nombre"}
    )
    fig_d.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig_d.update_layout(legend_title_text="", legend=dict(orientation="h", y=-0.2))
    _place_title(fig_d, "Nombre de retours par type de check-in")

    # Layout grid for the 4 charts
    r1c1, r1c2 = st.columns(2)
    r2c1, r2c2 = st.columns(2)
    r1c1.plotly_chart(fig_a, use_container_width=True)
    r1c2.plotly_chart(fig_b, use_container_width=True)
    r2c1.plotly_chart(fig_c, use_container_width=True)
    r2c2.plotly_chart(fig_d, use_container_width=True)

    st.markdown("---")

    # Pricing analysis
    st.subheader("Aperçu du parc (pricing)")
    cm1, cm2, cm3, cm4 = st.columns(4)

    with cm1:
        st.metric("Parc (pricing, scope)", f"{len(pricing_scoped):,}")
    with cm2:
        st.metric(
            "Prix moyen ($/jour)",
            f"{pricing_scoped[COL_PRICE_PER_DAY].mean():.0f}"
        )
    with cm3:
        st.metric(
            "Prix médian ($/jour)",
            f"{pricing_scoped[COL_PRICE_PER_DAY].median():.0f}"
        )
    with cm4:
        st.metric(
            "Écart-type ($/jour)",
            f"{pricing_scoped[COL_PRICE_PER_DAY].std():.0f}"
        )

    c1, c2 = st.columns(2)

    # E — price/day distribution (histogram)
    with c1:
        fig_hist = px.histogram(
            pricing_scoped,
            x=COL_PRICE_PER_DAY,
            nbins=30,
            marginal="violin",
            labels={COL_PRICE_PER_DAY: "Prix par jour ($)"}
        )
        fig_hist.update_layout(plot_bgcolor="white")
        _place_title(fig_hist, "Distribution des prix par jour")
        st.plotly_chart(fig_hist, use_container_width=True)

    # F — price/day by car type (boxplot)
    with c2:
        if "car_type" in pricing_scoped.columns:
            fig_box = px.box(
                pricing_scoped,
                x=COL_CAR_TYPE,
                y=COL_PRICE_PER_DAY,
                points="outliers",
                labels={
                    "rental_price_per_day": "Prix par jour ($)",
                    "car_type": "Type de véhicule"
                }
            )
            fig_box.update_layout(plot_bgcolor="white", xaxis_tickangle=-30)
            _place_title(fig_box, "Prix par jour selon type de véhicule")
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Colonne 'car_type' absente — Boxplot non disponible.")
