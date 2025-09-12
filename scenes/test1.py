from __future__ import annotations
from manim import *
import numpy as np

class PendulumTwoCycle(Scene):
    """
    微小振動×弾性衝突：同一平面・同じ支点・同じ長さ l の二振り子
    - 衝突は底点（theta=0）のみ
    - 接線方向1次元弾性衝突を角速度に適用（v_tau = l * omega）
    - 小振幅なので両者の固有角周波数は同じ omega = sqrt(g/l)
    - 2衝突で速度パターンが完全に元通り（厳密2周期）
    """

    def construct(self):
        # ---------- 物理パラメータ ----------
        g = 9.8
        l = 3.0
        m1 = 2.0   # 青（重い）
        m2 = 1.0   # 緑（軽い）
        omega0 = np.sqrt(g / l)
        T = 2 * np.pi / omega0

        # 初期条件（t=0 は「衝突直前」ではなく「衝突の瞬間」）
        # 衝突直前の接線速度 (v1, v2) = (u, 0) を想定
        # 衝突直後に弾性衝突公式を適用して、そこから運動開始
        u = 1.0  # 規格化された接線速度（描画に程よい大きさ）。実際のスケールは相対的でOK
        omega1 = u / l  # 角速度（接線速度 v = l * omega）
        omega2 = 0.0
        theta1 = 0.0
        theta2 = 0.0

        # 弾性衝突（接線方向）を角速度に適用する関数
        def collide(om1, om2):
            # v = l*omega なので l は両辺で約され、角速度にそのまま1次元弾性衝突を適用してよい
            v1, v2 = om1, om2
            v1p = ((m1 - m2) / (m1 + m2)) * v1 + (2 * m2 / (m1 + m2)) * v2
            v2p = (2 * m1 / (m1 + m2)) * v1 + ((m2 - m1) / (m1 + m2)) * v2
            return v1p, v2p

        # t=0 でまず衝突を適用（以降は自由運動→底点同時到達→衝突…の繰り返し）
        omega1, omega2 = collide(omega1, omega2)

        # ---------- 画面ジオメトリ ----------
        self.camera.background_color = "#0e1117"  # ダーク
        pivot = ORIGIN + UP * 2.5  # 支点
        scale = 1.0                # 表示スケール（本質に無関係）

        # ロッド（線）とおもり（円）
        rod1 = Line(pivot, pivot + l * scale * DOWN, stroke_width=4, color=BLUE_E)
        rod2 = Line(pivot, pivot + l * scale * DOWN, stroke_width=4, color=GREEN_E)

        r1 = 0.14 * np.sqrt(m1)  # 半径 ~ sqrt(m) に比例させ視覚化
        r2 = 0.14 * np.sqrt(m2)
        bob1 = Circle(radius=r1, color=BLUE_E, fill_opacity=1.0).set_fill(BLUE_E)
        bob2 = Circle(radius=r2, color=GREEN_E, fill_opacity=1.0).set_fill(GREEN_E)

        # 初期配置（theta=0）
        def angle_to_point(theta):
            # 支点から長さ l の円弧上（theta=0 が真下）
            return pivot + l * scale * (np.sin(theta) * RIGHT - np.cos(theta) * DOWN)

        rod1.put_start_and_end_on(pivot, angle_to_point(theta1))
        rod2.put_start_and_end_on(pivot, angle_to_point(theta2))
        bob1.move_to(rod1.get_end())
        bob2.move_to(rod2.get_end())

        # ラベル
        label = VGroup(
            Tex(r"$m_1=2m$", color=BLUE_E).scale(0.8),
            Tex(r"$m_2=m$", color=GREEN_E).scale(0.8),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL).shift(DOWN * 0.2 + RIGHT * 0.2)

        # エネルギーバー（運動エネルギーの瞬間値を表示）
        # K_i = 1/2 m_i (l^2 omega_i^2) + 1/2 m_i g l theta_i^2（小角近似のポテンシャルも足して総エネを出してもよい）
        # → ここでは“配分”の分かりやすさ重視で運動エネルギー K^kin のみを縦棒で表示
        bar_base = Axes(
            x_range=[0, 3, 1],
            y_range=[0, 1.0, 0.25],
            x_length=2.6,
            y_length=2.2,
            axis_config={"include_numbers": False, "stroke_color": GRAY_D, "stroke_opacity": 0.6},
        ).to_corner(UR).shift(LEFT * 0.3 + DOWN * 0.2)
        bar_title = Tex("Kinetic energy share", color=GRAY_B).scale(0.55).next_to(bar_base, UP, buff=0.2)

        # 棒（矩形）を手動で作って高さを更新
        bar1 = Rectangle(width=0.6, height=0.001, color=BLUE_E, fill_opacity=0.9).set_fill(BLUE_E)
        bar2 = Rectangle(width=0.6, height=0.001, color=GREEN_E, fill_opacity=0.9).set_fill(GREEN_E)
        # 配置（x=0.8 と x=2.0 あたり）
        x1 = bar_base.c2p(0.8, 0)
        x2 = bar_base.c2p(2.0, 0)
        bar1.move_to(x1, aligned_edge=DOWN)
        bar2.move_to(x2, aligned_edge=DOWN)
        bar1_label = Tex("$K_{1}$", color=BLUE_E).scale(0.5).next_to(bar1, DOWN, buff=0.1)
        bar2_label = Tex("$K_{2}$", color=GREEN_E).scale(0.5).next_to(bar2, DOWN, buff=0.1)

        # 衝突表示
        hit_glow = Dot(pivot + l * scale * DOWN, radius=0.12, color=YELLOW).set_opacity(0)

        # 画面に追加
        self.add(rod1, rod2, bob1, bob2, label, bar_base, bar_title, bar1, bar2, bar1_label, bar2_label, hit_glow)

        # ---------- 時間発展（アップデータ） ----------
        # 数値発展（Euler–Cromer: omega += -(g/l) * theta * dt , theta += omega * dt）
        # 衝突条件：abs(theta1) < eps && abs(theta2) < eps かつ 前フレームからのゼロ付近通過
        eps = 2e-2
        # 安定に見えるステップ（manim の dt は可変なので内部サブステップを切る）
        internal_dt = 1 / 240.0  # シミュレーション刻み
        speed = 1.0              # 実時間 vs 再生時間の倍率

        # 状態をクロージャで持つ
        state = {
            "theta1": theta1, "theta2": theta2,
            "omega1": omega1, "omega2": omega2,
            "t": 0.0,
            "collide_cooldown": 0.0,  # 直後の多重判定防止
        }

        # エネルギーバーの更新
        def update_bars():
            K1 = 0.5 * m1 * (l**2) * (state["omega1"]**2)
            K2 = 0.5 * m2 * (l**2) * (state["omega2"]**2)
            total = K1 + K2
            if total <= 1e-12:
                h1 = h2 = 0.0
            else:
                # 0〜1 に正規化表示
                h1 = np.clip(K1 / total, 0, 1)
                h2 = np.clip(K2 / total, 0, 1)
            # 高さを Axes の座標系に合わせて調整
            hmax = 1.0
            bar1.set_height(h1 * bar_base.y_length)  # y_length に合わせて縦方向を伸縮
            bar2.set_height(h2 * bar_base.y_length)
            bar1.move_to(x1, aligned_edge=DOWN)
            bar2.move_to(x2, aligned_edge=DOWN)

        update_bars()

        # ロッド＆ボブの配置更新
        def place_rods_and_bobs():
            th1 = state["theta1"]
            th2 = state["theta2"]
            p1 = angle_to_point(th1)
            p2 = angle_to_point(th2)
            rod1.put_start_and_end_on(pivot, p1)
            rod2.put_start_and_end_on(pivot, p2)
            bob1.move_to(p1)
            bob2.move_to(p2)

        place_rods_and_bobs()

        # 衝突エフェクト
        def flash_hit():
            hit_glow.move_to(angle_to_point(0.0))
            hit_glow.set_opacity(1.0)
            self.play(FadeOut(hit_glow, run_time=0.15, rate_func=linear))

        # アップデータ本体
        def evolve(mob, dt):
            # 可変 dt を内部で細分化
            steps = max(1, int(np.ceil((dt * speed) / internal_dt)))
            h = (dt * speed) / steps
            for _ in range(steps):
                # 力学（Euler–Cromer）
                state["omega1"] += -(g / l) * state["theta1"] * h
                state["omega2"] += -(g / l) * state["theta2"] * h
                prev1 = state["theta1"]
                prev2 = state["theta2"]
                state["theta1"] += state["omega1"] * h
                state["theta2"] += state["omega2"] * h
                state["t"] += h

                # 衝突クールダウン
                if state["collide_cooldown"] > 0.0:
                    state["collide_cooldown"] -= h

                # 衝突判定（底点付近で同時）
                near_zero = (abs(state["theta1"]) < eps) and (abs(state["theta2"]) < eps)
                crossing = (prev1 * state["theta1"] <= 0) and (prev2 * state["theta2"] <= 0)
                if near_zero and crossing and state["collide_cooldown"] <= 0.0:
                    # 弾性衝突：角速度に適用
                    state["omega1"], state["omega2"] = collide(state["omega1"], state["omega2"])
                    state["collide_cooldown"] = 0.08  # ほんの少しの待ち（多重判定防止）
                    # 視覚効果
                    flash_hit()

            # 形の更新
            place_rods_and_bobs()
            update_bars()

        # ダイナミクス開始
        dummy = VMobject()  # アップデータをぶら下げるためのダミー
        dummy.add_updater(evolve)
        self.add(dummy)

        # 説明テキスト
        caption = VGroup(
            Tex("Small-angle motion with perfectly elastic collisions", color=GRAY_B).scale(0.5),
            Tex("Energy splits $\\{1/9,\\;8/9\\}$ and returns after two hits", color=GRAY_B).scale(0.5),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(DL).shift(UP * 0.2 + RIGHT * 0.2)
        self.add(caption)

        # 再生：数周期ぶん
        self.wait(4 * T / 2)  # 2周期ぶん程度
        dummy.remove_updater(evolve)