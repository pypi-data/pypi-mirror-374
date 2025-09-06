from h2lib_tests import tfp
import pytest

from h2lib._h2lib import H2LibThread, H2Lib
from h2lib.distributed_sections import DistributedSections, LinkType
import numpy as np
from numpy import testing as npt
import matplotlib.pyplot as plt
from wetb.hawc2.htc_file import HTCFile


def test_distributed_sections():
    # apply force on tower and check deflected tower position
    with H2Lib(suppress_output=0) as h2:
        model_path = f"{tfp}DTU_10_MW/"
        htc_path = f"{tfp}DTU_10_MW/htc/DTU_10MW_RWT.htc"
        h2.init(htc_path=htc_path, model_path=model_path)

        ax = plt.figure().add_subplot(projection='3d')
        for i in [1, 2, 3]:
            # ds = DistributedSections(name='', link_type=1, link_id=i, nsec=50)
            ds = h2.get_distributed_sections(LinkType.BLADE, link_id=i)

            sec_pos, sec_tsg = h2.get_distributed_section_position_orientation(ds, mainbody_coo_nr=0)
            x, y, z = sec_pos.T
            ax.plot(y, x, -z, label=ds.name)
            for (x, y, z), tsg in zip(sec_pos, sec_tsg):
                for (ex, ey, ez), c in zip(tsg.T * 10, 'rgb'):
                    plt.plot([y, y + ey], [x, x + ex], [-z, -z - ez], c)
        plt.legend()
        plt.axis('equal')
        if 0:
            plt.show()
        ds = h2.get_distributed_sections(LinkType.BLADE, link_id=2)
        sec_pos, sec_tsg = h2.get_distributed_section_position_orientation(ds, mainbody_coo_nr=0)
        npt.assert_array_almost_equal(sec_pos[40], [70.58938502, -16.98280589, -77.95555399], 6)
        npt.assert_array_almost_equal(sec_tsg[40], [[0.49371347, 0.09098716, 0.86485163],
                                                    [0.12164175, 0.97750846, -0.17228029],
                                                    [-0.86107508, 0.19025917, 0.47154125]], 6)

        with pytest.raises(AssertionError, match=r"'missing' does not exist. Valid names are \['tower',"):
            h2.add_distributed_sections('missing', [0, .4, .8, 1])
        mbdy_name_dict = h2.get_mainbody_name_dict()
        mbdy_name_lst = list(mbdy_name_dict.keys())
        ds_dict = {mbdy_name: h2.add_distributed_sections(mbdy_name, [0, .4, .8, 1])
                   for mbdy_name in mbdy_name_lst}
        h2.initialize_distributed_sections()
        ds_dict['blade1_aero'] = h2.get_distributed_sections(LinkType.BLADE, 1)

        ax = plt.figure().add_subplot(projection='3d')
        for name, ds in ds_dict.items():
            sec_pos, sec_tsg = h2.get_distributed_section_position_orientation(ds, mbdy_name_dict['hub2'])
            x, y, z = sec_pos.T
            ax.plot(y, x, -z, label=name)
            for (x, y, z), tsg in zip(sec_pos, sec_tsg):
                for (ex, ey, ez), c in zip(tsg.T * 10, 'rgb'):

                    plt.plot([y, y + ey], [x, x + ex], [-z, -z - ez], c)

        plt.axis('equal')
        if 0:
            plt.show()

        # print(ds_lst[6].name, ds_lst[3].name)
        # mb_pos, b1_mb_tbg, b1_sec_pos, sec_tsb = h2.get_distributed_section_position_orientation(ds_lst[6])
        # hub_id = h2.get_mainbody_name_dict()['hub1']
        # print(hub_id)
        # print(h2.get_mainbody_position_orientation(hub_id))
        # print(b1_sec_pos[[0, -1]])

        sec_pos, sec_tsb = h2.get_distributed_section_position_orientation(ds_dict['blade1'])
        # print(np.round(mb_pos + [mb_tbg@sp for sp in sec_pos], 1).tolist())

        print(np.round(sec_pos, 1).tolist())
        npt.assert_array_almost_equal(sec_pos, [[-0.0, -6.9, -121.8],
                                                [0.8, -5.7, -156.4],
                                                [0.4, -5.8, -190.9],
                                                [0.1, -6.5, -208.2]], 1)

        sec_pos, sec_tsb = h2.get_distributed_section_position_orientation(ds_dict['blade1_aero'])

        idx = [0, 10, 20, 30, 40, 49]
        print(np.round(sec_pos[idx], 2).tolist())
        npt.assert_array_almost_equal(sec_pos[idx], [[1.3, -6.61, -121.78],
                                                     [1.37, -6.27, -130.32],
                                                     [2.33, -5.65, -152.69],
                                                     [1.51, -5.61, -179.95],
                                                     [0.86, -6.2, -201.24],
                                                     [0.29, -6.53, -208.25]], 2)

        frc = np.zeros((4, 3))
        frc[:, 1] = 100000
        h2.set_distributed_section_force_and_moment(ds_dict['tower'], sec_frc=frc, sec_mom=np.zeros((4, 3)))

        h2.run(2)
        for ds in ds_dict.values():
            sec_pos, sec_tsb = h2.get_distributed_section_position_orientation(ds)
            x, y, z = sec_pos.T
            ax.plot(y, x, -z, '--', label=ds.name)
        plt.legend()
        plt.axis('scaled')
        if 0:
            plt.show()
        plt.close('all')
        np.set_printoptions(linewidth=200)
        sec_pos, sec_tsb = h2.get_distributed_section_position_orientation(ds_dict['tower'])
        # print(np.round(mb_pos + [mb_tbg@sp for sp in sec_pos], 1).tolist())

        npt.assert_array_almost_equal(sec_pos, [[0.0, 0.0, 0.0],
                                                [-0.0, 0.7, -46.2],
                                                [-0.0, 2.4, -92.5],
                                                [0.0, 3.5, -115.6]], 1)


def test_distributed_sections_static_solver():
    with H2Lib() as h2:
        model_path = f"{tfp}DTU_10_MW/"
        htc_path = f"{tfp}DTU_10_MW/htc/DTU_10MW_RWT_only_tower.htc"
        h2.init(htc_path=htc_path, model_path=model_path)
        ds = h2.add_distributed_sections(mainbody_name='tower', section_relative_position=[0, .5, 1])
        h2.initialize_distributed_sections()

        ax = plt.figure().add_subplot(projection='3d')

        def draw(label, ref):
            pos = h2.get_mainbody_nodes_state(mainbody_nr=1, state='pos')
            # print(label, np.round(pos[-1], 4).tolist())
            npt.assert_array_almost_equal(pos[-1], ref, 4)
            ax.plot(*pos.T, marker='.', label=label)
            ax.set_zlim([0, -120])

        pos = h2.get_mainbody_nodes_state(mainbody_nr=1, state='pos')

        draw('initial', [0.0, 0.0, -115.63])

        frc = np.zeros((3, 3))
        frc[:, 1] = 100000
        h2.set_distributed_section_force_and_moment(ds, sec_frc=frc, sec_mom=frc * 0)
        h2.solver_static_run(reset_structure=True)
        draw('set frc + static solver', [0.0, 1.8295, -115.6123])
        c2_def = np.concatenate([pos, pos[:, :1]], 1)
        c2_def[:, 0] = np.r_[np.arange(0, 60, 10), np.arange(50, 0, -10)]
        h2.set_c2_def('tower', c2_def)
        draw('set_c2_def', [10.0, 0.1184, -115.6296])
        h2.solver_static_run(reset_structure=True)
        draw('static solver', [10.2777, 2.8085, -115.5066])
        h2.set_distributed_section_force_and_moment(ds, sec_frc=-frc, sec_mom=frc * 0)
        h2.solver_static_run(reset_structure=True)
        draw('set -frc + static solver', [10.2859, -2.8064, -115.5011])
        if 0:
            plt.legend()
            plt.show()
        else:
            plt.close('all')


def test_set_distributed_section_force_and_moment_coo():
    with H2Lib() as h2:
        model_path = f"{tfp}DTU_10_MW/"
        htc = HTCFile(model_path + "htc/DTU_10MW_RWT_only_tower.htc")
        htc.new_htc_structure.orientation.base.body_eulerang = 0, 0, 90
        htc.save(model_path + "htc/DTU_10MW_RWT_only_tower_rot90.htc")
        print(htc)
        h2.init(htc_path=htc.filename, model_path=model_path)
        ds = h2.add_distributed_sections(mainbody_name='tower', section_relative_position=[0, .5, 1])
        h2.initialize_distributed_sections()

        ax = plt.figure().add_subplot(projection='3d')

        def draw(label, ref):
            h2.solver_static_run()
            pos = h2.get_mainbody_nodes_state(mainbody_nr=1, state='pos')
            print(label, np.round(pos[-1], 4).tolist())
            ax.plot(*pos.T, marker='.', label=label)
            npt.assert_array_almost_equal(pos[-1], ref, 4)

        draw('init', [0.0, 0.0, -115.6281])
        frc = np.zeros((3, 3))
        frc[:, 1] = 2e6
        h2.set_distributed_section_force_and_moment(ds, sec_frc=frc, sec_mom=frc * 0)
        draw('frc_y_global', [-0.0, 34.7544, -109.7119])

        h2.set_distributed_section_force_and_moment(ds, sec_frc=frc, sec_mom=frc * 0, mainbody_coo_nr=1)
        draw('frc_y_tower', [-34.7545, 0.0, -109.7119])

        if 0:
            ax.axis('equal')
            ax.set_zlim([0, -120])
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z')
            ax.plot([0, 0], [0, 10], label='global y')
            ax.plot([0, -10], [0, 0], label='tower y')
            ax.legend()
            plt.show()
        else:
            plt.close('all')
