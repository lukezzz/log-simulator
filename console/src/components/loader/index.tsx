import './style.css';

interface IProps {
  spinning: boolean;
  fullScreen?: boolean;
}

const Loader: React.FC<IProps> = ({ spinning, fullScreen = true }) => {
  return (
    <div
      className={`loader ${!spinning ? 'hidden' : ''} ${fullScreen ? 'fullScreen' : ''}`}
    >
      <div className={'wrapper'}>
        <div className={'inner'} />
        <div className={'text'}>Loading...</div>
      </div>
    </div>
  );
};

export default Loader;