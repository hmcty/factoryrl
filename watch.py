import dreamerv3
from factory import FactoryEnv
from dreamerv3 import embodied
from embodied.envs import from_gym
import pygame
import numpy as np

def render_pygame(obs, env_no, envs, screen, clock, fps):
    image = envs.render()
    screen.blit(pygame.surfarray.make_surface(image[0]), (0, 0))
    pygame.display.flip()
    clock.tick(fps)

def main():
    config = embodied.Config(dreamerv3.configs['defaults'])
    config = config.update(dreamerv3.configs['medium'])
    config = config.update({
        'logdir': '~/logdir/run2',
        'run.train_ratio': 64,
        'run.log_every': 90,  # Seconds
        'batch_size': 10,
        'jax.prealloc': False,
        'encoder.mlp_keys': '$^',
        'decoder.mlp_keys': '$^',
        'encoder.cnn_keys': 'image',
        'decoder.cnn_keys': 'image',
        # 'jax.platform': 'cpu',
    })
    config = embodied.Flags(config).parse()

    logdir = embodied.Path(config.logdir)
    step = embodied.Counter()
    logger = embodied.Logger(step, [
        embodied.logger.TerminalOutput(),
        embodied.logger.JSONLOutput(logdir, 'metrics.jsonl'),
        embodied.logger.TensorBoardOutput(logdir),
        # embodied.logger.WandBOutput(logdir.name, config),
        # embodied.logger.MLFlowOutput(logdir.name),
    ])
    config = config.update(run=config.run.update(from_checkpoint='~/logdir/run2/checkpoint.ckpt'))
    args = embodied.Config(
        **config.run, logdir=config.logdir,
        batch_steps=config.batch_size * config.batch_length)
    print(args.from_checkpoint)
    pygame.init()
    screen = pygame.display.set_mode((512, 512))
    clock = pygame.time.Clock()

    env = FactoryEnv()  # Replace this with your Gym env.
    env = from_gym.FromGym(env, obs_key='image')
    env = dreamerv3.wrap_env(env, config)
    env = embodied.BatchEnv([env], parallel=False)
    fps = 30.
    on_step_cb = lambda obs, env_no: render_pygame(obs, env_no, env, screen, clock, fps)
    
    step = embodied.Counter()
    agent = dreamerv3.Agent(env.obs_space, env.act_space, step, config)

    embodied.run.eval_only(agent, env, logger, args, on_step_cb)

if __name__ == "__main__":
    main()
