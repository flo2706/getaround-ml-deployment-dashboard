# analysis_page.py
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

from common import (
    COLOR_CI,
    COL_CHECKIN,
    COL_DELAY,
    COL_GAP,
    COL_PREV_ID,
    COL_RENTAL_ID,
    COL_STATE,
    CLIP_MAX,
    CLIP_MIN,
    STATUS_COLORS,
    read_logo,
    apply_scope,
    pick_value,
    build_curves_masked_solved,
    get_plotly_theme,
    place_title as _place_title,
)

# Apply shared Plotly theme
pio.templates["getaround"] = get_plotly_theme()
pio.templates.default = "getaround"


# Helpers
def _legend_bottom(fig, y: float = -0.25) -> None:
    """Put legend horizontally below the plot."""
    fig.update_layout(legend_title_text="", legend=dict(orientation="h", y=y))


# Page
def page_analyse_retards(
    df_delay_full: pd.DataFrame,
    dataset_pricing: pd.DataFrame,
) -> None:
    """
    Operational analysis page.

    Steps
    -----
    1) Global delay distribution.
    2) Propagation to next rental.
    3) Product buffer rule (gap < threshold) simulation.
    4) Business impact (masked share, solved conflicts, revenue proxy).

    """

    # Data preparation
    df_delay = df_delay_full.copy()

    if COL_DELAY not in df_delay.columns:
        st.warning(f"Colonne '{COL_DELAY}' manquante.")
        return

    df_delay["delay_clipped"] = pd.to_numeric(
        df_delay[COL_DELAY], errors="coerce"
    ).clip(CLIP_MIN, CLIP_MAX)

    # Header
    svg = read_logo("getaround_logo.svg")
    if svg:
        st.markdown(
            f"<div style='text-align:center'>{svg}</div>", unsafe_allow_html=True
        )

    st.markdown(
        "<h2 style='text-align:center;'>Analyse des retards & choix du seuil</h2>",
        unsafe_allow_html=True,
    )

    st.caption(f"BORNAGE ACTIF : [{CLIP_MIN}, {CLIP_MAX}] mn")

    st.info(
        "Périmètre d’affichage : `state='ended'`. "
        "Règle produit : **location masquée** si `gap < seuil`. "
        "Conflits **résolus** : conflits historiques (`delay > gap`) "
        "qui auraient été masqués (`gap < seuil`).",
        icon="ℹ️",
    )
    st.markdown("---")

    # Global scope selector
    scope = st.radio(
        "Portée",
        ["Toutes les voitures", "Connect uniquement", "Mobile uniquement"],
        horizontal=True,
    )
    df_scoped, dataset_pricing = apply_scope(df_delay, dataset_pricing, scope)
    st.markdown("---")

    # PART 1 — Distribution des retards
    st.divider()
    st.subheader("Partie 1 - Distribution des retards")

    ended = df_scoped[df_scoped[COL_STATE] == "ended"].copy()
    col_a, col_b, col_c = st.columns([1.2, 1.8, 0.8])

    if ended.empty:
        st.info("Aucune location terminée dans le périmètre actuel.")
    else:
        # Counts
        n_ok = int((ended["delay_clipped"] <= 0).sum())
        n_late = int((ended["delay_clipped"] > 0).sum())
        n_nan = int(ended["delay_clipped"].isna().sum())

        observed = ended.dropna(subset=["delay_clipped"]).copy()
        late_only = ended[ended["delay_clipped"] > 0].copy()

        median_delay = (
            float(late_only["delay_clipped"].median()) if not late_only.empty else 0.0
        )
        pct_gt_60_among_lates = (
            (late_only["delay_clipped"] > 60).mean() * 100.0
            if not late_only.empty
            else 0.0
        )
        pct_gt_60_among_observed = (
            (observed["delay_clipped"] > 60).mean() * 100.0
            if not observed.empty
            else 0.0
        )

        # Pie
        with col_a:
            labels = ["En retard", "À l'heure / en avance", "Non renseigné"]
            values = [n_late, n_ok, n_nan]
            pie_colors = {
                "En retard": STATUS_COLORS["En retard"],
                "À l'heure / en avance": STATUS_COLORS["À l'heure"],
                "Non renseigné": STATUS_COLORS["Non renseigné"],
            }

            fig_pie = px.pie(
                names=labels,
                values=values,
                hole=0.35,
                color=labels,
                color_discrete_map=pie_colors,
            )
            _place_title(fig_pie, "Statut du retour (avec Non renseigné)")
            _legend_bottom(fig_pie)
            fig_pie.update_traces(
                sort=False, textposition="outside", textinfo="percent+label"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            st.caption(
                "Non renseigné = "
                f"{n_nan:,} ligne(s), soit "
                f"{n_nan / len(ended) * 100:.1f} % des ‘ended’. "
                f"(Scope : **{scope}**, bornage : **[{CLIP_MIN}, {CLIP_MAX}] mn**)"
            )

        # Histogram (late only)
        with col_b:
            if late_only.empty:
                st.info("Aucun retard > 0 minute dans le périmètre.")
            else:
                fig_hist = px.histogram(
                    late_only,
                    x="delay_clipped",
                    nbins=60,
                    range_x=[0, CLIP_MAX],
                    labels={"delay_clipped": "Retard au checkout (mn, borné)"},
                )
                _place_title(fig_hist, "Distribution des retards (minutes)")
                _legend_bottom(fig_hist)
                fig_hist.update_layout(plot_bgcolor="white")
                st.plotly_chart(fig_hist, use_container_width=True)

        # KPIs
        with col_c:
            st.metric("Retard médian", f"{median_delay:.1f} min")
            st.metric(
                "Retard > 1h (parmi les retards)", f"{pct_gt_60_among_lates:.1f} %"
            )
            st.caption(
                "Retard > 1h parmi toutes les ‘ended’ observées : "
                f"{pct_gt_60_among_observed:.1f} %"
            )

    st.markdown("---")

    # PART 2 — Propagation du retard à la location suivante
    st.divider()
    st.subheader("Partie 2 - Impact des retards sur la location suivante")

    y_max_vis = 1000

    ended_scoped = df_scoped[df_scoped[COL_STATE] == "ended"].copy()
    ended_scoped = ended_scoped[
        ended_scoped[COL_CHECKIN].isin(["mobile", "connect"])
    ].copy()

    if {COL_RENTAL_ID, COL_PREV_ID}.issubset(
        ended_scoped.columns
    ) and not ended_scoped.empty:
        next_map = (
            ended_scoped.dropna(subset=[COL_PREV_ID])
            .set_index(COL_PREV_ID)[COL_RENTAL_ID]
            .to_dict()
        )
        ended_scoped["next_rental_id"] = ended_scoped[COL_RENTAL_ID].map(next_map)
    else:
        ended_scoped["next_rental_id"] = np.nan

    delay_map = ended_scoped.set_index(COL_RENTAL_ID)["delay_clipped"].to_dict()
    has_next = ended_scoped.dropna(subset=["next_rental_id"]).copy()

    if not has_next.empty:
        has_next["next_rental_id"] = pd.to_numeric(
            has_next["next_rental_id"], errors="coerce"
        ).astype("Int64")
        has_next["next_delay"] = has_next["next_rental_id"].map(delay_map)
        has_next = has_next.dropna(subset=["delay_clipped", "next_delay"]).copy()
        has_next = has_next[has_next["next_delay"] >= 0].copy()
        has_next["next_delay"] = has_next["next_delay"].clip(0, y_max_vis)

        pct_late_next = (has_next["next_delay"] > 0).mean() * 100.0
        avg_next_delay = has_next.loc[has_next["next_delay"] > 0, "next_delay"].mean()

        df_plot = has_next.copy()
        fig_scatter = px.scatter(
            df_plot,
            x="delay_clipped",
            y="next_delay",
            color=COL_CHECKIN,
            color_discrete_map=COLOR_CI,
            labels={
                "delay_clipped": "Retard au checkout (mn, borné)",
                "next_delay": "Retard de la suivante (mn, borné)",
                COL_CHECKIN: "Type de check-in",
            },
        )
        _place_title(
            fig_scatter,
            "Propagation du retard : location actuelle → location suivante (périmètre ended uniquement)",
        )
        _legend_bottom(fig_scatter)

        fig_scatter.add_hline(y=0, line_dash="dash", line_color="#999", opacity=0.6)
        fig_scatter.add_vline(x=0, line_dash="dash", line_color="#999", opacity=0.6)
        fig_scatter.update_layout(plot_bgcolor="white")

        st.plotly_chart(fig_scatter, use_container_width=True)

        c1, c2 = st.columns(2)
        c1.metric("Retards au pointage suivant", f"{pct_late_next:.1f} %")
        c2.metric("Retard moyen si en retard", f"{(avg_next_delay or 0):.1f} mn")

        st.caption(
            "Périmètre : `state='ended'`, flux `mobile/connect`. "
            f"Bornages X=[{CLIP_MIN},{CLIP_MAX}] et Y=[0,{y_max_vis}] mn. "
            "Seuls les couples A→B valides sont conservés."
        )
    else:
        st.info(
            "Aucune paire A→B exploitable dans le périmètre actuel "
            "(ended + next_rental_id)."
        )

    st.markdown("---")

    # PART 3 — Impact du délai (gap) entre deux locations
    st.divider()
    st.subheader("Partie 3 - Impact du délai entre deux locations")

    preset = st.segmented_control("Presets", options=[10, 30, 60, 90], default=60)
    threshold_min = st.slider(
        "Seuil (buffer) en minutes",
        min_value=0,
        max_value=180,
        value=int(preset),
        step=5,
    )
    st.caption(
        "Le buffer masque les créneaux où l'écart entre deux locations est inférieur au seuil défini ci-dessus."
    )

    df_gap = df_scoped.dropna(subset=["delay_clipped", COL_GAP]).copy()
    df_gap["gap"] = df_gap[COL_GAP]
    df_gap = df_gap[df_gap[COL_CHECKIN].isin(["mobile", "connect"])].copy()

    if df_gap.empty:
        st.info("Aucune ligne avec gap connu dans le périmètre.")
        return

    df_gap["was_conflict"] = df_gap["delay_clipped"] > df_gap["gap"]

    loss_curve, solved_curve = build_curves_masked_solved(df_gap)

    color_curves = {
        "Masquées mobile (%)": COLOR_CI.get("mobile", "#1f77b4"),
        "Masquées connect (%)": COLOR_CI.get("connect", "#ff7f0e"),
        "Évités mobile (%)": COLOR_CI.get("mobile", "#1f77b4"),
        "Évités connect (%)": COLOR_CI.get("connect", "#ff7f0e"),
    }

    left, right = st.columns([3, 1])

    # Masked share vs threshold
    with left:
        fig_loss = px.line(
            loss_curve,
            x="Seuil (min)",
            y="value",
            color="variable",
            markers=True,
            color_discrete_map=color_curves,
        )
        _place_title(fig_loss, "🔻 % de locations masquées vs seuil (règle produit)")
        _legend_bottom(fig_loss)

        fig_loss.update_yaxes(
            range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix=" %"
        )
        fig_loss.add_vline(
            x=threshold_min, line_dash="dash", line_color="#666", opacity=0.7
        )
        fig_loss.add_vrect(
            x0=0, x1=threshold_min, fillcolor="#777", opacity=0.06, line_width=0
        )
        fig_loss.update_traces(hovertemplate="%{y:.1f} % à %{x} min")
        fig_loss.add_annotation(
            x=threshold_min,
            yref="paper",
            y=1.05,
            text=f"Seuil = {threshold_min} mn",
            showarrow=False,
        )
        fig_loss.add_annotation(
            xref="paper",
            x=0,
            yref="paper",
            y=-0.22,
            text=f"Basé sur {len(df_gap):,} lignes où l'écart (gap) est connu.",
            showarrow=False,
        )
        fig_loss.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig_loss, use_container_width=True)

    with right:
        st.metric(
            f"Masquées mobile ({threshold_min} mn)",
            f"{pick_value(loss_curve, 'Masquées mobile (%)', threshold_min):.2f} %",
        )
        st.metric(
            f"Masquées connect ({threshold_min} mn)",
            f"{pick_value(loss_curve, 'Masquées connect (%)', threshold_min):.2f} %",
        )
        st.caption(
            f"Basé sur {len(df_gap):,} lignes où l'écart (*gap*) entre locations successives est connu."
        )

    st.divider()

    left, right = st.columns([3, 1])

    # Solved conflicts vs threshold
    with left:
        fig_solved = px.line(
            solved_curve,
            x="Seuil (min)",
            y="value",
            color="variable",
            markers=True,
            color_discrete_map=color_curves,
        )
        _place_title(fig_solved, " % de conflits historiques évités vs seuil")
        _legend_bottom(fig_solved)

        fig_solved.update_yaxes(
            range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix=" %"
        )
        fig_solved.add_vline(
            x=threshold_min, line_dash="dash", line_color="#666", opacity=0.7
        )
        fig_solved.add_vrect(
            x0=0, x1=threshold_min, fillcolor="#777", opacity=0.06, line_width=0
        )
        fig_solved.update_traces(hovertemplate="%{y:.1f} % à %{x} min")
        fig_solved.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig_solved, use_container_width=True)

    with right:
        st.metric(
            f"Conflits évités mobile ({threshold_min} mn)",
            f"{pick_value(solved_curve, 'Évités mobile (%)', threshold_min):.2f} %",
        )
        st.metric(
            f"Conflits évités connect ({threshold_min} mn)",
            f"{pick_value(solved_curve, 'Évités connect (%)', threshold_min):.2f} %",
        )
        st.caption(
            "✔️ *Masquées (%)* : part des locations qui seraient cachées si gap < seuil.\n"
            "✔️ *Évités (%)* : part des conflits historiques évités grâce à ce masquage."
        )

    csv_export = pd.concat(
        [
            loss_curve.assign(type_courbe="Masquées (%)"),
            solved_curve.assign(type_courbe="Évités (%)"),
        ],
        ignore_index=True,
    )

    st.download_button(
        label="⬇️ Télécharger les courbes (CSV)",
        data=csv_export.to_csv(index=False, sep=";", encoding="utf-8-sig"),
        file_name=f"courbes_getaround_{threshold_min}mn.csv",
        mime="text/csv",
    )

    # PART 4 — Simulation business finale
    st.markdown("---")
    st.divider()
    st.subheader("Partie 4 - Simulation business du buffer choisi")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_duration_days = st.number_input(
            "Durée moyenne d’une location (jours)",
            min_value=0.5,
            max_value=14.0,
            value=1.5,
            step=0.5,
            help="Hypothèse business utilisée pour estimer la valeur unitaire.",
        )

    with col2:
        loss_rate = (
            st.slider(
                "% des conflits entraînant une perte de CA",
                min_value=0,
                max_value=100,
                value=60,
                step=5,
                help="Dans X % des conflits, on perd réellement du CA (annulation, geste co.).",
            )
            / 100.0
        )

    with col3:
        if ("rental_price_clipped" in dataset_pricing.columns) or (
            "rental_price_per_day" in dataset_pricing.columns
        ):
            price_col = (
                "rental_price_clipped"
                if "rental_price_clipped" in dataset_pricing.columns
                else "rental_price_per_day"
            )
        else:
            st.warning(
                "Aucune colonne de prix trouvée ('rental_price_clipped' ou 'rental_price_per_day')."
            )
            return

        if (
            scope == "Connect uniquement"
            and "has_getaround_connect" in dataset_pricing.columns
        ):
            mean_daily_price = dataset_pricing.loc[
                dataset_pricing["has_getaround_connect"],
                price_col,
            ].mean()
        elif (
            scope == "Mobile uniquement"
            and "has_getaround_connect" in dataset_pricing.columns
        ):
            mean_daily_price = dataset_pricing.loc[
                ~dataset_pricing["has_getaround_connect"],
                price_col,
            ].mean()
        else:
            mean_daily_price = dataset_pricing[price_col].mean()

        if np.isnan(mean_daily_price):
            mean_daily_price = dataset_pricing[price_col].mean()

        mean_daily_price = float(mean_daily_price)
        st.metric("Prix moyen utilisé ($/jour)", f"{mean_daily_price:.0f}")

    # Eligible pool
    if COL_GAP not in df_scoped.columns:
        st.info(f"La colonne '{COL_GAP}' n’est pas disponible.")
        return

    eligible = df_scoped.dropna(subset=["delay_clipped", COL_GAP]).copy()
    eligible["gap"] = eligible[COL_GAP].astype(float)
    if COL_STATE in eligible.columns:
        eligible = eligible[eligible[COL_STATE] == "ended"].copy()

    if eligible.empty:
        st.info("Aucune ligne éligible (retard & gap connus dans 'ended').")
        return

    # KPIs
    affected_mask = eligible["gap"] < threshold_min
    n_eligible = int(len(eligible))
    n_affected = int(affected_mask.sum())
    pct_affected = (n_affected / n_eligible * 100.0) if n_eligible else 0.0

    conflict_before = eligible["delay_clipped"] > eligible["gap"]
    resolved_mask = conflict_before & (eligible["gap"] < threshold_min)

    n_problematic = int(conflict_before.sum())
    n_resolved = int(resolved_mask.sum())
    pct_resolved = (n_resolved / n_problematic * 100.0) if n_problematic else 0.0

    avg_booking_value = mean_daily_price * avg_duration_days
    lost_gmv = n_affected * avg_booking_value * loss_rate
    baseline_gmv = n_eligible * avg_booking_value
    share_revenue_affected = (lost_gmv / baseline_gmv * 100.0) if baseline_gmv else 0.0

    k1, k2, k3 = st.columns(3)
    k1.metric("Part du CA potentiellement affectée", f"{share_revenue_affected:.1f} %")
    k2.metric("Locations masquées", f"{n_affected:,} ({pct_affected:.1f} %)")
    k3.metric("Conflits historiques résolus", f"{n_resolved:,} ({pct_resolved:.1f} %)")
