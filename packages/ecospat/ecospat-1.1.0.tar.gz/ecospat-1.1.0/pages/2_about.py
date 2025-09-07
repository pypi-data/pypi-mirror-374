import solara
from solara import component

from pathlib import Path
import pandas as pd


@solara.component
def Page():
    solara.Style(Path("solara/assets/custom.css"))

    with solara.Column(align="center", gap="1rem"):
        # Title (centered, bold)
        solara.Markdown("# **The importance of range edges**")

        # Subtitle
        solara.Markdown(
            "##_The non-contiguous range of species can be categorized into ecologically informative edges based on their location and distribution._",
            style={"text-align": "center"},
        )

        image_url_range_overview = "images/range_dynamics_head.png"
        solara.Image(image_url_range_overview, width="800px")

        solara.Markdown(
            "An important question in ecology and biodiversity science is how much genetic, phenotypic, and functional variation exists among individuals of the same species. This variation is a critical conservation priority, but proves difficult to readily identify across large scales.",
            style={"text-align": "center"},
        )

        solara.Markdown(
            '####Hampe & Petit (<a href="https://onlinelibrary.wiley.com/doi/10.1111/j.1461-0248.2005.00739.x" target="_blank">2005</a>) first introduced a conceptual model characterizing differences in populations and their dynamics based on latitudinal range.',
            style={"text-align": "center"},
        )

        solara.Markdown(
            'This model has since been built upon by Woolbright et al. (<a href="https://www.sciencedirect.com/science/article/abs/pii/S0169534714001062" target="_blank">2014</a>) to incorporate eco-evolutionary dynamics important to the interaction structure of communities.'
            # style={"text-align": "center"},
        )

        solara.Markdown(
            "####To explore how to categorize these range edges using _ecospat_,checkout [how-to](/how-to)."
        )

        solara.Markdown("## Range Edges")

        range_base_image = "images/range_only.png"

        with solara.Column(align="center"):
            solara.Image(range_base_image, width="200px")

        solara.Markdown(
            "By categorizing populations into range edges, we can understand how populations will respond to climate change via individual variation and assign conservation priority based on management goals."
        )

        solara.Markdown(
            "### However, species ranges are differentially expanding and contracting rapidly in the Global North and South under climate change."
        )

        solara.Markdown(
            "Range movement dynamics also affect variation important to determining persistence and conservation. For example, poleward movement, following climate envelopes favors the persistence of leading edge populations, while leading edges are more threatened under stable conditions."
        )

        # Right column: fake table made with rows in a Grid
        ImageWithToggleMarkdown()

        solara.Markdown(
            "### Many populations are expanding poleward; however, not all range edges are moving in the same way."
        )
        solara.Markdown(
            """
            Range edges can:

            - Expand poleward together
            - Contract equatorward together
            - Pull apart (leading edge expanding and trailing edge contracting)
            - Reabsorb (leading and trailing edges moving back into core zone of admixture)
            - Stabilize
            """
        )

        range_options = "images/range_movement_types.png"
        solara.Image(range_options, width="800px")

        solara.Markdown(
            "### Range movement is also affected by changes in population density."
        )

        solara.Markdown(
            "High leading edge abundance facilitates poleward movement, while evenly distributed individuals contribute towards range stability."
        )
        ImageWithToggleMarkdownPopulation()

        solara.Markdown(
            """
        #### If we can identify
        1. range edges
        2. range movement patterns
        3. population dynamics within and across range edges

        we can better understand how species have responded to past climate change and infer their potential for persistence at individual, population, community, and ecosystem levels. For instance, populations across a species’ range may gain or lose relative importance for maintaining ecosystem services and functions depending on their abundance and the persistence of their individuals. If a keystone species is characterized by a pull-apart range dynamic, declining core populations, edge populations with low propagule pressure, and reduced individual persistence, the ecosystem that depends on it may start to disassemble in a systematic way. Such individual to ecosystem-level consequences are not revealed by examining any single variable in isolation (e.g., range dynamics, population dynamics, etc).

        Until recently, these insights were largely unattainable due to limitations of scale and data availability. Historically, southward range shifts in species from the Global South have been underrepresented, and tools to analyze these dynamics lag behind those developed for northern species.

        However, global occurrence data spanning both small and large spatial and temporal scales makes this possible.
        """
        )

        solara.Markdown(
            "## _ecospat_ uses GBIF historical and modern data to identify range and population dynamics through time"
        )

        map_hist_image = "images/historic_map.jpg"
        map_mod_image = "images/modern_map.jpg"

        with solara.Row(justify="start"):
            solara.Markdown(
                "### North America",
                style={"text-align": "left"},
            )
        with solara.Row(gap="2rem", justify="center"):
            # Left image with caption
            with solara.Column():
                solara.Markdown(
                    "**Historic Range _Populus angustifolia_**",
                    style={"text-align": "center"},
                )
                solara.Image(map_hist_image, width="600px")

            # Right image with caption
            with solara.Column():
                solara.Markdown(
                    "**Modern Range _Populus angustifolia_**",
                    style={"text-align": "center"},
                )
                solara.Image(map_mod_image, width="600px")

        image_url_summary = "images/summary.png"
        solara.Image(image_url_summary, width="800px")

        asia_map_hist_image = "images/lonicera_historic.png"
        asia_map_mod_image = "images/lonicera_modern.png"

        with solara.Row(justify="start"):
            solara.Markdown(
                "### Asia",
                style={"text-align": "left"},
            )
        with solara.Row(gap="2rem", justify="center"):
            # Left image with caption
            with solara.Column():
                solara.Markdown(
                    "**Historic Range _Lonicera japonica_**",
                    style={"text-align": "center"},
                )
                solara.Image(asia_map_hist_image, width="600px")

            # Right image with caption
            with solara.Column():
                solara.Markdown(
                    "**Modern Range _Lonicera japonica_**",
                    style={"text-align": "center"},
                )
                solara.Image(asia_map_mod_image, width="600px")

        asia_summary = "images/lonicera_dynamic.png"
        solara.Image(asia_summary, width="800px")

        sa_map_hist_image = "images/chamaecrista_historic.png"
        sa_map_mod_image = "images/chamaecrista_modern.png"

        with solara.Row(justify="start"):
            solara.Markdown(
                "### Central and Southern Africa",
                style={"text-align": "left"},
            )
        with solara.Row(gap="2rem", justify="center"):
            # Left image with caption
            with solara.Column():
                solara.Markdown(
                    "**Historic Range _Chamaecrista mimosoides_**",
                    style={"text-align": "center"},
                )
                solara.Image(sa_map_hist_image, width="600px")

            # Right image with caption
            with solara.Column():
                solara.Markdown(
                    "**Modern Range _Chamaecrista mimosoides_**",
                    style={"text-align": "center"},
                )
                solara.Image(sa_map_mod_image, width="600px")

        sa_summary = "images/chamaecrista_dynamic.png"
        solara.Image(sa_summary, width="800px")

        australia_map_hist_image = "images/acacia_historic.png"
        australia_map_mod_image = "images/acacia_modern.png"

        with solara.Row(justify="start"):
            solara.Markdown(
                "### Oceania",
                style={"text-align": "left"},
            )
        with solara.Row(gap="2rem", justify="center"):
            # Left image with caption
            with solara.Column():
                solara.Markdown(
                    "**Historic Range _Acacia pycnantha_**",
                    style={"text-align": "center"},
                )
                solara.Image(australia_map_hist_image, width="600px")

            # Right image with caption
            with solara.Column():
                solara.Markdown(
                    "**Modern Range _Acacia pycnantha_**",
                    style={"text-align": "center"},
                )
                solara.Image(australia_map_mod_image, width="600px")

        acacia_summary = "images/acacia_dynamic.png"
        solara.Image(acacia_summary, width="800px")

        solara.Markdown(
            "###**Propagule Pressure** = Range Edge x Directional Movement x Distance to Source x Distance Decay x Population Size x Population Density Change",
            style={"text-align": "center", "width": "1200px"},
        )
        solara.Markdown(
            ""
            "Propagule pressure describes the likelihood of individuals arriving from nearby populations, depending on local population dynamics and range-edge position. Leading populations gaining individuals and expanding northward have high propagule pressure, while isolated trailing populations losing individuals have low propagule pressure. Core populations under stable conditions typically experience moderate propagule pressure."
        )

        raster_map = "images/raster_map.png"

        with solara.Column():
            solara.Markdown(
                "**Propagule Pressure _Populus angustifolia_**",
                style={"text-align": "center"},
            )
            solara.Image(raster_map, width="600px")

        solara.Markdown(
            "### **Individual Persistence** = Baseline Mortality x Range Edge x Directional Movement x (1 + Propagule Pressure)"
        )
        solara.Markdown(
            "While certain range edges harbor unique genetic, phenotypic, and functional variation, the individuals contributing to this variation do not have the same probability of persisting."
        )

        solara.Markdown(
            "Individual persistence describes the probability of an individual surviving through time, influenced by species mortality, local population dynamics, and location. For example a Loblolly pine (_Pinus taeda_) individual with a baseline mortality of 0.8% (meaning 99.2% of individuals survive per year) in the north of a core zone moving northward has a higher persistence than an individual in the southern part of the same population, an individual in a trailing population, or an individual of another species, such as sugar maple (_Acer saccharum_) with a higher baseline mortality of 2%."
        )

        pinus_persistence = "images/pinus_persistence.jpg"

        acer_persistence = "images/acer_persistence.jpg"

        with solara.Column():
            solara.Markdown(
                "**Individual Persistence _Pinus taeda_ - Baseline survival 99.2%**",
                style={"text-align": "center"},
            )
            solara.Image(pinus_persistence, width="800px")

            solara.Markdown(
                "**Individual Persistence _Acer saccharum_ - Baseline survival 98%**",
                style={"text-align": "center"},
            )
            solara.Image(acer_persistence, width="800px")

        with solara.Column(
            style={
                "text-align": "left",
                "padding-bottom": "3vh",
                "margin-bottom": "50px",
            }
        ):
            solara.Markdown(
                "# _ecospat_ bridges the gap between community science and community conservation",
                style={"text-align": "center"},
            )
            solara.Markdown(
                "###Local information on species can empower community-led conservation efforts."
            )
            solara.Markdown(
                "While many citizen scientists care about the species in their communities, currently there are few tools that allow individuals to translate that awareness into meaningful action. By understanding the expected persistence of individuals both locally and in surrounding areas, _ecospat_ provides information that enable targeted, community-level management of species — effectively bridging the gap between knowledge and on-the-ground action."
            )
            solara.Markdown(
                "### Please see [use-case](/use-case) to see _ecospat_ in action.",
                style={"text-align": "center"},
            )


import solara

filter_mode = solara.reactive("Poleward Movement")
filter_mode_pop = solara.reactive("Poleward Movement")


@solara.component
def ImageWithToggleMarkdown():

    # Single toggle for the content
    solara.ToggleButtonsSingle(
        value=filter_mode,
        values=["Poleward Movement", "Stability"],
        style={"display": "flex", "justifyContent": "center", "marginBottom": "10px"},
    )

    # Layout: image + content
    with solara.Row(
        style={
            "display": "flex",
            "alignItems": "flex-start",
            "justifyContent": "center",
            "gap": "20px",
            "flexWrap": "wrap",
        }
    ):
        # Left: Image
        image_to_show = (
            "images/conserve_priority_north.png"
            if filter_mode.value == "Poleward Movement"
            else "images/conserve_priority_stable.png"
        )
        solara.Image(image_to_show, width="300px")

        # Right: Conditional Markdown
        with solara.Column(style={"maxWidth": "600px"}):
            if filter_mode.value == "Poleward Movement":
                solara.Markdown(
                    """
                    ### Leading: Poleward edges.
                    - **Low** among population genetic variation
                    - **Low** functional trait diversity

                    ### Core: Central zone of admixture.
                    - Stability

                    ### Trailing: Equatorward edges.
                    - **High** among population genetic variation
                    - **High** functional trait diversity

                    ### Relict: Latitudinal and longitudinal outliers.
                    - High genetic variation and functional trait diversity
                    - Low stability
                    """
                )
            else:
                solara.Markdown(
                    """
                    ### Leading: Poleward edges.
                    - **High** among population genetic variation
                    - **High** functional trait diversity

                    ### Core: Central zone of admixture.
                    - Stability

                    ### Trailing: Equatorward edges.
                    - **Moderate** among population genetic variation
                    - **Low** functional trait diversity

                    ### Relict: Latitudinal and longitudinal outliers.
                    - High genetic variation and functional trait diversity
                    - Low stability
                    """
                )


@solara.component
def ImageWithToggleMarkdownPopulation():

    # Single toggle for the content
    solara.ToggleButtonsSingle(
        value=filter_mode_pop,
        values=["Poleward Movement", "Stability"],
        style={"display": "flex", "justifyContent": "center", "marginBottom": "10px"},
    )

    # Layout: image + content
    with solara.Row(
        style={
            "display": "flex",
            "alignItems": "flex-start",
            "justifyContent": "center",
            "gap": "20px",
            "flexWrap": "wrap",
        }
    ):

        # Right: Conditional Markdown
        with solara.Column(style={"maxWidth": "600px"}):
            if filter_mode_pop.value == "Poleward Movement":
                solara.Markdown(
                    """
                    ### Leading: Increasing

                    ### Core: Stable

                    ### Trailing: Decreasing

                    ### Relict: Decreasing
                    """
                )
            else:
                solara.Markdown(
                    """
                    ### Leading: Stable

                    ### Core: Increasing

                    ### Trailing: Stable

                    ### Relict: Decreasing
                    """
                )
                # Left: Image
        image_to_show = (
            "images/North Gray.png"
            if filter_mode_pop.value == "Poleward Movement"
            else "images/Stability Gray.png"
        )
        solara.Image(image_to_show, width="300px")
