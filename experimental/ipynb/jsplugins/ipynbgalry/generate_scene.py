from galry import *
s = SceneCreator()

x = np.linspace(-1., 1., 1000)
y = np.sin(20 * x) * .2 - .5

x = np.vstack((x, x))
y = np.vstack((y, y + 1))

color = np.array([[1., 0., 0., 1.],
                  [0., 0., 1., 1.]], dtype=np.float32)

s.add_visual(PlotVisual, x, y, color=color)
scene_json = s.serialize()

print type(scene_json)

# write JS file
# f = open('scene.js', 'w')
# f.write("scene_json = '%s';" % scene_json)
# f.close()

